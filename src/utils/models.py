
from sqlalchemy import Column, DateTime, Integer, func, ForeignKey
from src.config.database import Base


class BaseModel(Base):
    __abstract__ = True

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), default=None, nullable=True, index=True)