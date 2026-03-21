from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Index,
    Integer,
    String,
    ForeignKey,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from database import Base

# class Quest(Base):
#     __tablename__ = "quests"

#     quest_id = Column(String, primary_key=True, index=True)
#     title = Column(String, nullable=False)
#     description = Column(Text)
#     start_scene_id = Column(String, nullable=False)

#     scenes = relationship("QuestScene", back_populates="quest", cascade="all, delete-orphan")
#     user_progress = relationship("UserQuestProgress", back_populates="quest")

#     def get_scene(self, scene_id: str) -> Optional['QuestScene']:
#         """Получить сцену по ID"""
#         return next((scene for scene in self.scenes if scene.scene_id == scene_id), None)

# class QuestScene(Base):
#     __tablename__ = "quest_scenes"

#     scene_id = Column(String, primary_key=True, index=True)  # "chapter_1", "chapter_5_1_10_1"
#     quest_id = Column(String, ForeignKey("quests.quest_id"), nullable=False, index=True)

#     legend = Column(Text, nullable=False)
#     task = Column(Text, nullable=False)
#     has_clue = Column(Boolean, default=False)
#     clue = Column(Text)
#     expected_result = Column(JSONB, default=dict)
#     tags = Column(JSONB, default=list)  # ["select", "join", "update"]

#     is_branching = Column(Boolean, default=False)
#     next_scene_id = Column(String, nullable=True)
#     branches = Column(JSONB, default=dict)  # {"1": "chapter_5_1", "2": "chapter_5_2"}
#     default_fail_scene = Column(String, nullable=True)

#     quest = relationship("Quest", back_populates="scenes")

#     __table_args__ = (
#         Index('ix_quest_scenes_quest_id_scene_id', quest_id, scene_id),
#     )


class UserQuestProgress(Base):
    __tablename__ = "users_quest"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True, index=True)
    quest_id = Column(String, primary_key=True, index=True)
    current_scene_id = Column(String, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="quest_progress")
