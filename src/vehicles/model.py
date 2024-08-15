from src.utils.models import BaseModel
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship



class UserVehicle(BaseModel):
    __tablename__ =  'user_vehicles'


    id = Column(Integer, primary_key=True)
    vehicle_name = Column(String, nullable=False)
    vehicle_number = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="vehicles")
