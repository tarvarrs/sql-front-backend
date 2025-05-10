from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    easy_tasks_solved = Column(Integer, default=0)
    medium_tasks_solved = Column(Integer, default=0)
    hard_tasks_solved = Column(Integer, default=0)

    user = relationship("User", back_populates="progress")
