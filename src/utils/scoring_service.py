from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User

class ScoringService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_points(self, user_id: int, points: int) -> None:
        """Начисляет баллы пользователю."""
        if points <= 0:
            return
        await self.session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(total_score=User.total_score + points)
        )

    async def deduct_points(self, user_id: int, penalty: int) -> None:
        """Списывает баллы."""
        if penalty <= 0:
            return
        await self.session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(total_score=User.total_score - penalty)
        )
