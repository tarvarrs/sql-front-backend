# Регистрируем все модели для корректной работы SQLAlchemy
from src.models.achievement import (
    Achievement,
    UserAchievementProgress,
    UsersAchievements,
)
from src.models.progress import UserProgress
from src.models.user import PasswordHash

from .task import Task, TaskSolved
from .user import User

__all__ = [
    "User",
    "Task",
    "TaskSolved",
    # ... остальные модели
]
