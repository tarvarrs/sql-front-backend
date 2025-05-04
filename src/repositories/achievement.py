from collections import defaultdict
from typing import Dict, List
from sqlalchemy import select, outerjoin
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.achievement import Achievement, UserAchievement

class AchievementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_achievements_grouped(self, user_id: int) -> Dict[str, List[dict]]:
        stmt = (
            select(
                Achievement.category_name,
                Achievement.achievement_id,
                Achievement.icon,
                Achievement.name,
                Achievement.description,
                Achievement.historical_info,
                UserAchievement.achievement_id.isnot(None).label("is_earned")
            )
            .select_from(Achievement)
            .join(
                UserAchievement,
                (Achievement.achievement_id == UserAchievement.achievement_id) & 
                (UserAchievement.user_id == user_id),
                isouter=True
            )
            .order_by(Achievement.category_name, Achievement.achievement_id)
        )
        
        result = await self.session.execute(stmt)
        
        grouped = defaultdict(list)
        for row in result:
            grouped[row.category_name].append({
                "achievement_id": row.achievement_id,
                "icon": row.icon,
                "name": row.name,
                "description": row.description,
                "historical_info": row.historical_info,
                "is_earned": bool(row.is_earned)
            })
        
        return dict(grouped)
