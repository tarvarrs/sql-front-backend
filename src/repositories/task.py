from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.task import Task, TaskSolved

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tasks_count(self) -> dict:
        """Возвращает количество задач по уровням сложности"""
        result = await self.session.execute(
            select(Task.mission_id, func.count(Task.task_id))
            .group_by(Task.mission_id)
        )
        counts = {0: 0, 1: 0, 2: 0}  # mission_id: 0-easy, 1-medium, 2-hard
        for mission_id, count in result.all():
            counts[mission_id] = count
        
        return {
            "easy_tasks_total": counts[0],
            "medium_tasks_total": counts[1],
            "hard_tasks_total": counts[2]
        }

    async def get_task_info(self, mission_id: int, task_id: int) -> Task:
        """Возвращает информацию о задаче"""
        result = await self.session.execute(
            select(Task).where(
                (Task.mission_id == mission_id) & 
                (Task.task_id == task_id)
            )
        )
        return result.scalars().first()

    async def add_solved_task(self, user_id: int, task_id: int) -> TaskSolved:
        """Добавляет запись о решенной задаче"""
        solved_task = TaskSolved(user_id=user_id, task_id=task_id)
        self.session.add(solved_task)
        await self.session.commit()
        return solved_task