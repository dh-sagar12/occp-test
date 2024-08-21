from fastapi import APIRouter, Depends
from src.auth.models import User
from src.config.database import get_db
from src.endpoints.models import VehicleCreate
from sqlalchemy.orm import Session
from src.utils.auth_utils import get_current_user
from src.vehicles.model import UserVehicle

router = APIRouter(tags=['Vehicles'])

@router.post("/vehicles")
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db), user : User  = Depends(get_current_user)):
    db_vehicle = UserVehicle(
        vehicle_name=vehicle.vehicle_name,
        vehicle_number=vehicle.vehicle_number,
        description=vehicle.description,
        user_id= user.id
    )
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return {
        'detail': 'vehicle added '
    }

