from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Achievement(Base):
    __tablename__ = "achievements"

    achievement_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String, nullable=False)
    icon = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    historical_info = Column(String, nullable=False)

    users = relationship("UserAchievement", back_populates="achievement")

class UserAchievement(Base):
    __tablename__ = "users_achievements"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    achievement_id = Column(Integer, ForeignKey("achievements.achievement_id"), primary_key=True)

    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="users")
