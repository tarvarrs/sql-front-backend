from sqlalchemy import (
    Column,
    Integer,
    PrimaryKeyConstraint,
    String,
    ForeignKey
)
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
    tag = Column(String)
    required_count = Column(Integer)

    users = relationship(
        "UsersAchievements", 
        back_populates="achievement",
        cascade="all, delete-orphan"
    )
    progress_records = relationship(
        "UserAchievementProgress",
        back_populates="achievement",
        cascade="all, delete-orphan"
    )


class UsersAchievements(Base):
    __tablename__ = "users_achievements"

    user_id = Column(Integer,
                    ForeignKey("users.user_id",ondelete='CASCADE'),
                    primary_key=True)
    achievement_id = Column(Integer,
                            ForeignKey(
                                "achievements.achievement_id",
                                ondelete='CASCADE'
                                ),
                            primary_key=True)

    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="users")


class UserAchievementProgress(Base):
    __tablename__ = "user_achievement_progress"
    __table_args__ = tuple(
        PrimaryKeyConstraint('user_id', 'achievement_id')
    )
    user_id = Column(
        Integer,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        primary_key=True
    )
    achievement_id = Column(
        Integer,
        ForeignKey('achievements.achievement_id', ondelete='CASCADE'),
        primary_key=True
    )
    current_count = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="achievement_progress")
    achievement = relationship("Achievement", back_populates="progress_records")