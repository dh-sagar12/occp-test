
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, APIRouter
import asyncio
import logging
import websockets
import datetime 
# Set up logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()
router = APIRouter(tags=['Ocpp'])

charging_status = {}
client_connections = {}

@router.post("/start_charging/{charge_point_id}")
async def start_charging(charge_point_id: str):
    charging_status[charge_point_id] = 0
    return {"message": f"Charging started for {charge_point_id}"}

@router.websocket("/ocpp/{charge_point_id}")
async def websocket_endpoint(websocket: WebSocket, charge_point_id: str):
    await websocket.accept()
    try:
        async with websockets.connect(f'ws://localhost:9002/{charge_point_id}') as central_ws:
            while True:
                data = await central_ws.recv()
                await websocket.send_text(data)
    except websockets.exceptions.ConnectionClosed:
        logging.info(f"Connection to central WebSocket server closed.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        await websocket.close()
        
        
