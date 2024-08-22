from src.utils.models import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class EVChargerMachine(BaseModel):
    __tablename__ = "ev_charger_machines"

    id = Column(Integer, primary_key=True)
    machine_model_number  =  Column(String, unique=True, nullable=False)
    latitude = Column(String, nullable=False)
    longitute = Column(String, nullable=False)
    


