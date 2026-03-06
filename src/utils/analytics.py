from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_event import UserEvent


async def log_user_event(
    session: AsyncSession,
    user_id: int,
    event_type: str,
    task_id: int = None,
    payload: dict = None,
):
    """
    Запись событий в TimescaleDB
    """
    event = UserEvent(
        user_id=user_id, event_type=event_type, task_id=task_id, payload=payload or {}
    )
    session.add(event)
    await session.commit()
