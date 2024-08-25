from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.utils.models import BaseModel

class EVChargerMachine(BaseModel):
    __tablename__ = "ev_charger_machines"

    id = Column(Integer, primary_key=True)
    machine_model_number = Column(String, unique=True, nullable=False)
    latitude = Column(String, nullable=False)
    longitude = Column(String, nullable=False)
    
    charge_points = relationship("ChargePoint", back_populates="machine")


class ChargePoint(BaseModel):
    __tablename__ = "charge_points"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    machine_id = Column(Integer, ForeignKey("ev_charger_machines.id"), nullable=False)
    
    machine = relationship("EVChargerMachine", back_populates="charge_points")
