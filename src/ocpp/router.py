from fastapi import FastAPI, WebSocket, APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result, call
from ocpp.v16.enums import RegistrationStatus, ChargePointStatus
import asyncio
import uuid
from src.vehicles.model import UserVehicle
from src.machine.models import EVChargerMachine
from src.config.database import get_db
from src.utils.auth_utils import get_current_user
from src.auth.models import User

app = FastAPI()
router = APIRouter(tags=['Ocpp'])

class ChargingSession:
    def __init__(self, session_id: str, device_id: str, vehicle_id: int, user_id: int):
        self.session_id = session_id
        self.device_id = device_id
        self.vehicle_id = vehicle_id
        self.user_id = user_id
        self.charging_percentage = 0
    
    def update_charging_percentage(self):
        if self.charging_percentage < 100:
            self.charging_percentage += 10
        return self.charging_percentage

charging_sessions = {}

class ChargePoint(cp):
    @on("BootNotification")
    async def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        return call_result.BootNotification(
            current_time="2024-08-22T10:00:00Z",
            interval=10,
            status=RegistrationStatus.accepted
        )

    @on("StartTransaction")
    async def on_start_transaction(self, connector_id, id_tag, **kwargs):
        transaction_id = str(uuid.uuid4())
        return call_result.StartTransaction(
            transaction_id=transaction_id,
            id_tag_info={"status": "Accepted"}
        )

    @on("StopTransaction")
    async def on_stop_transaction(self, transaction_id, **kwargs):
        return call_result.StopTransaction(id_tag_info={"status": "Accepted"})

@app.websocket("/ws/ocpp/{device_id}")
async def ocpp_websocket(websocket: WebSocket, device_id: str):
    await websocket.accept()
    charge_point = ChargePoint(device_id, websocket)
    asyncio.create_task(charge_point.start())

    while True:
        if device_id in charging_sessions:
            session = charging_sessions[device_id]
            percentage = session.update_charging_percentage()
            if percentage <= 100:
                await websocket.send_json({"charging_percentage": percentage})
            else:
                del charging_sessions[device_id]
                break
        await asyncio.sleep(5)

@router.post("/initiate-charging-session")
async def initiate_charging_session(device_id: str, vehicle_id: int, user_id: int):
    session_id = str(uuid.uuid4())
    charging_sessions[device_id] = ChargingSession(session_id, device_id, vehicle_id, user_id)
    return {"session_id": session_id, "detail": "Charging session initiated"}


# API to handle connection between mobile and EV charger device
@router.post("/ocpp/connect")
def connect_device(
    device_id: str = Query(...), 
    user_id: int = Query(...), 
    vehicle_id: int = Query(...), 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    # Validate the logged-in user
    if user.id != user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to initiate this session.")

    # Validate the vehicle belongs to the user
    vehicle = db.query(UserVehicle).filter_by(id=vehicle_id, user_id=user_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found or not associated with this user.")

    # Validate the EV charger device exists
    charger_device = db.query(EVChargerMachine).filter_by(id=device_id).first()
    if not charger_device:
        raise HTTPException(status_code=404, detail="EV charger device not found.")

    # Initiate the OCPP connection (mocked for now)
    session_id = f"session_{device_id}_{user_id}_{vehicle_id}"
    
    # Mimic real-time charging data (for demo)
    charging_data = {"charging_percentage": 0}
    
    # Simulate the charging process (In real implementation, this would use websockets)
    for i in range(0, 101, 20):
        charging_data["charging_percentage"] = i
        # Normally this would be sent over a WebSocket connection
        print(f"Charging: {charging_data['charging_percentage']}%")

    return {"session_id": session_id, "message": "OCPP session initiated", "charging_data": charging_data}

app.include_router(router)
