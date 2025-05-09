# Регистрируем все модели для корректной работы SQLAlchemy
from .user import User
from .task import Task, TaskSolved
from src.models.user import PasswordHash
from src.models.progress import UserProgress
from src.models.achievement import Achievement, UsersAchievements, UserAchievementProgress

__all__ = [
    'User',
    'Task',
    'TaskSolved',
    # ... остальные модели
]