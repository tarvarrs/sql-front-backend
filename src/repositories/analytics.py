# src/repositories/analytics_repo.py
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_thinking_time_stats(session: AsyncSession, user_id: int):
    query = text("""
        SELECT 
            task_id,
            EXTRACT(EPOCH FROM (
                MIN(timestamp) FILTER (WHERE event_type = 'task_attempt') - 
                MIN(timestamp) FILTER (WHERE event_type = 'task_started')
            )) as seconds
        FROM user_events
        WHERE user_id = :uid
        GROUP BY task_id
        HAVING 
            MIN(timestamp) FILTER (WHERE event_type = 'task_attempt') IS NOT NULL 
            AND MIN(timestamp) FILTER (WHERE event_type = 'task_started') IS NOT NULL
            AND MIN(timestamp) FILTER (WHERE event_type = 'task_attempt') > MIN(timestamp) FILTER (WHERE event_type = 'task_started')
    """)

    result = await session.execute(query, {"uid": user_id})
    return [{"task_id": row.task_id, "seconds_to_start": row.seconds} for row in result]
