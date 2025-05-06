from sqlalchemy import Column, Integer, String, ForeignKey, Identity
from sqlalchemy.orm import relationship, declarative_base
from database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, Identity(start=1, increment=1), primary_key=True, index=True)
    login = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    total_score = Column(Integer, default=0)

    password_rel = relationship("PasswordHash", back_populates="user_rel", uselist=False, cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user", uselist=False)
    achievements = relationship(
        "UsersAchievements",
        back_populates="user",
        cascade="all, delete-orphan")
    achievement_progress = relationship(
        "UserAchievementProgress",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    solved_tasks = relationship("TaskSolved", back_populates="user")


class PasswordHash(Base):
    __tablename__ = "password_hashes"

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, unique=True)
    password_hash = Column(String, nullable=False)

    user_rel = relationship("User", back_populates="password_rel")
