from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from database import Base

class UserEvent(Base):
    __tablename__ = "user_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    user_id = Column(Integer, nullable=False, index=True)
    task_id = Column(Integer, nullable=True, index=True)  # Может быть NULL
    
    event_type = Column(String, nullable=False, index=True)
    payload = Column(JSON, default={})