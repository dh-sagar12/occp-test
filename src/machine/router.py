from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.machine.models import EVChargerMachine
from src.endpoints.models import EVChargerMachineCreate, EVChargerMachineUpdate, EVChargingMachines

router = APIRouter(tags=['Machine'])

@router.get("/ev-charger-machines")
def get_ev_charger_machines(db: Session = Depends(get_db)):
    machines = db.query(EVChargerMachine).all()
    return [
        EVChargingMachines(id=machine.id, model_number =  machine.machine_model_number, longitude= machine.longitude, latitude=  machine.latitude) for machine in machines
    ]

@router.get("/ev-charger-machines/{id}")
def get_ev_charger_machine(id: int, db: Session = Depends(get_db)):
    machine = db.query(EVChargerMachine).get(id)
    if not machine:
        raise HTTPException(status_code=404, detail="EV charger machine not found")
    return EVChargingMachines(id=machine.id, model_number =  machine.machine_model_numberc, longitude= machine.longitude, latitude=  machine.latitude)

@router.post("/ev-charger-machines")
def create_ev_charger_machine(machine: EVChargerMachineCreate, db: Session = Depends(get_db)):

    try:
        new_machine = EVChargerMachine(
            machine_model_number=machine.machine_model_number,
            latitude=machine.latitude,
            longitude=machine.longitude
        )
        db.add(new_machine)
        db.commit()
        return {
        "result": "successful"
         }
    except Exception as e:
        raise HTTPException(status_code = 500, detail=f"{e}")
    

@router.put("/ev-charger-machines/{id}")
def update_ev_charger_machine(id: int, machine: EVChargerMachineUpdate, db: Session = Depends(get_db)):
    existing_machine = db.query(EVChargerMachine).get(id)
    if not existing_machine:
        raise HTTPException(status_code=404, detail="EV charger machine not found")
    existing_machine.machine_model_number = machine.machine_model_number
    existing_machine.latitude = machine.latitude
    existing_machine.longitude = machine.longitude
    db.commit()
    db.refresh(existing_machine)
    return {
        "result": "success"
    }
