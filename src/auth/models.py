from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.utils.models import BaseModel
from sqlalchemy.ext.hybrid import hybrid_property


class User(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username  =  Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String(50), nullable=False, index=True)
    last_name = Column(String(50), nullable=False, index=True)
    
    vehicles  =  relationship("UserVehicle", back_populates='user')

    @hybrid_property
    def name(self):
        return self.last_name + " " + self.first_name
