from fastapi import HTTPException
from sqlalchemy import select, func, outerjoin, exists, update, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.user import UserRepository
from src.models.progress import UserProgress
from src.models.user import User
from src.models.task import Task, TaskSolved
from src.repositories.achievement import AchievementRepository
from src.models.clue import PurchasedClue
from typing import Dict, List
from collections import defaultdict
from config import settings


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
        solved_task = TaskSolved(user_id=user_id, task_global_id=task_id)
        self.session.add(solved_task)
        await self.session.commit()
        return solved_task

    async def get_all_tasks_grouped(self) -> Dict[int, List[dict]]:
        """Возвращает все задания, сгруппированные по mission_id"""
        result = await self.session.execute(
            select(
                Task.mission_id,
                Task.task_id,
                Task.task_global_id,
                Task.title
            ).order_by(Task.mission_id, Task.task_id)
        )

        grouped = defaultdict(list)
        for task in result.all():
            grouped[task.mission_id].append({
                "task_id": task.task_id,
                "task_global_id": task.task_global_id,
                "title": task.title
            })
        
        return dict(grouped)
    
    async def get_all_tasks_grouped_with_status(self, user_id: int) -> Dict[int, List[dict]]:
        req = (
            select(
                Task.mission_id,
                Task.task_id,
                Task.task_global_id,
                Task.title,
                TaskSolved.task_global_id.isnot(None).label("is_solved")
            )
            .select_from(Task)
            .join(
                TaskSolved,
                (Task.task_global_id == TaskSolved.task_global_id) &
                (TaskSolved.user_id == user_id),
                isouter=True
            )
            .order_by(Task.mission_id, Task.task_id)
        )
        result = await self.session.execute(req)
        grouped = defaultdict(list)
        for row in result.all():
            grouped[row.mission_id].append({
                "task_id": row.task_id,
                "task_global_id": row.task_global_id,
                "title": row.title,
                "is_solved": bool(row.is_solved)
            })
        return dict(grouped)

    async def get_user_solved_tasks(self, user_id: int) -> Dict[int, List[dict]]:
        """Возвращает решенные пользователем задания, сгруппированные по mission_id"""
        result = await self.session.execute(
            select(
                Task.mission_id,
                Task.task_id,
                Task.task_global_id,
                Task.title
            )
            .join(TaskSolved, Task.task_global_id == TaskSolved.task_global_id)
            .where(TaskSolved.user_id == user_id)
            .order_by(Task.mission_id, Task.task_id)
        )
        
        grouped = defaultdict(list)
        for task in result.all():
            grouped[task.mission_id].append({
                "task_id": task.task_id,
                "task_global_id": task.task_global_id,
                "title": task.title
            })
        
        return dict(grouped)

    async def get_tasks_grouped_by_mission(self, user_id: int) -> Dict[int, List[dict]]:
        stmt = (
            select(
                Task.mission_id,
                Task.task_id,
                Task.task_global_id,
                Task.title,
                TaskSolved.task_global_id.isnot(None).label("is_solved")
            )
            .select_from(Task)
            .join(
                TaskSolved,
                (Task.task_global_id == TaskSolved.task_global_id) & 
                (TaskSolved.user_id == user_id),
                isouter=True
            )
            .order_by(Task.mission_id, Task.task_id)
        )
        
        result = await self.session.execute(stmt)
        
        grouped = defaultdict(list)
        for row in result:
            grouped[row.mission_id].append({
                "task_id": row.task_id,
                "task_global_id": row.task_global_id,
                "title": row.title,
                "is_solved": bool(row.is_solved)
            })
        
        return dict(grouped)

    async def get_task_info_with_status(
        self, 
        mission_id: int, 
        task_id: int,
        user_id: int
        ) -> tuple[Task, bool]:
        """Возвращает задачу и статус решения пользователем"""
        task_result = await self.session.execute(
            select(Task)
            .where(
                (Task.mission_id == mission_id) & 
                (Task.task_id == task_id)
            )
        )
        task = task_result.scalars().first()
        
        if not task:
            return None, False
        
        solved_result = await self.session.execute(
            select(exists()
            .where(
                (TaskSolved.task_global_id == task.task_global_id) &
                (TaskSolved.user_id == user_id))
                )
            )
        is_solved = solved_result.scalar()
        
        return task, is_solved

    async def check_and_reward_task(
        self,
        user_id: int,
        mission_id: int,
        task_id: int,
        is_correct: bool
    ) -> dict:

        task = await self.session.execute(
            select(Task.task_global_id)
            .where(
                (Task.mission_id == mission_id) &
                (Task.task_id == task_id)
            )
        )
        task_global_id = task.scalar()
        if not task_global_id:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        already_solved = await self.session.execute(
            select(exists().where(
                (TaskSolved.user_id == user_id) &
                (TaskSolved.task_global_id == task_global_id)
            ))
        )
        already_solved = already_solved.scalar()
        points_earned = 0
        points_penalty = 0
        message = ""

        if is_correct:
            if not already_solved:
                points = settings.TASK_POINTS[mission_id] if mission_id < len(settings.TASK_POINTS) else 0
                points_earned = points
                await self.session.execute(
                    update(User)
                    .where(User.user_id == user_id)
                    .values(total_score=User.total_score + points)
                )
                self.session.add(TaskSolved(
                    user_id=user_id,
                    task_global_id=task_global_id
                ))
                progress_field = [
                    "easy_tasks_solved",
                    "medium_tasks_solved", 
                    "hard_tasks_solved"
                ][mission_id]
                await self.session.execute(
                    update(UserProgress)
                    .where(UserProgress.user_id == user_id)
                    .values(**{progress_field: getattr(UserProgress, progress_field) + 1})
                )
                message = f"Правильно! Заработано {points} баллов"
                await self.clear_purchased_clues(user_id, task_global_id)
            else:
                message = f"Правильно! За повторное решение баллы не начисляются"
        else:
            if not already_solved:
                points_penalty = int(settings.TASK_POINTS[mission_id] * 0.1) if mission_id < len(settings.TASK_POINTS) else 0
                await self.session.execute(
                    update(User)
                    .where(User.user_id == user_id)
                    .values(total_score=User.total_score - points_penalty)
                )
                message = f"Ответ неверный! Списано {points_penalty} баллов"
            else:
                message = f"Ответ неверный! За повторное решение баллы не списываются"
        await self.session.commit()

        task_tags_result = await self.session.execute(
            select(Task.tags).where(
                (Task.mission_id == mission_id) &
                (Task.task_id == task_id)
            )
        )
        task_tags = task_tags_result.scalar() or []
        
        if is_correct and task_tags:
            achievement_repo = AchievementRepository(self.session)
            awarded_achievements = await achievement_repo.check_and_award_achievements(
                user_id=user_id,
                task_tags=task_tags
            )
        else:
            awarded_achievements = []
        
        await self.session.commit()

        user_repo = UserRepository(self.session)
        user_progress = await user_repo.get_user_progress_by_id(user_id)

        return {
            "was_solved_before": already_solved,
            "points_earned": points_earned,
            "points_penalty": points_penalty,
            "message": message,
            "awarded_achievements": awarded_achievements,
            "current_points": user_progress.total_score
        }
    async def purchase_clue(
            self,
            user_id: int,
            task_global_id: int,
            clue_type: int,
            cost: int
    ) -> bool:
        user = await self.session.get(User, user_id)
        if user.total_score < cost:
            raise HTTPException(
                status_code=400,
                detail="Недостаточно баллов для покупки подсказки"
            )
        user.total_score -= cost

        self.session.add(PurchasedClue(
            user_id=user_id,
            task_global_id=task_global_id,
            clue_type=clue_type
        ))
        await self.session.commit()
        return True

    async def clear_purchased_clues(
            self,
            user_id: int,
            task_global_id: int
    ):
        await self.session.execute(
            delete(PurchasedClue).where(
                (PurchasedClue.user_id == user_id) &
                (PurchasedClue.task_global_id == task_global_id)
            )
        )
