from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.progress import UserProgress

class ProgressRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_progress(self, user_id: int) -> UserProgress | None:
        result = await self.session.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        return result.scalars().first()
    
    async def update_progress(
            self,
            user_id: int,
            easy: int=0,
            medium: int=0,
            hard: int=0
    ) -> UserProgress:
        progress = await self.get_user_progress(user_id)
        if not progress:
            progress = UserProgress(user_id=user_id)
            self.session.add(progress)
        
        progress.easy_tasks_solved += easy
        progress.medium_tasks_solved += medium
        progress.hard_tasks_solved += hard

        await self.session.commit()
        return progress
