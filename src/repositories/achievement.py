from collections import defaultdict
from typing import Dict, List
from sqlalchemy import select, outerjoin, exists, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from src.models.achievement import Achievement, UserAchievementProgress, UsersAchievements

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
                UsersAchievements.achievement_id.isnot(None).label("is_earned")
            )
            .select_from(Achievement)
            .join(
                UsersAchievements,
                (Achievement.achievement_id == UsersAchievements.achievement_id) & 
                (UsersAchievements.user_id == user_id),
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
    async def check_and_award_achievements(
            self,
            user_id: int,
            task_tags: list[str]
    ) -> list[dict]:
        if not task_tags:
            return []
        req = select(Achievement).where(
            Achievement.tag.in_(task_tags),
            Achievement.required_count.is_not(None)
        )
        result = await self.session.execute(req)
        achievements = result.scalars().all()
        awarded_achievements = []
        for ach in achievements:
            has_achievement = await self.session.execute(
                select(exists().where(
                    (UsersAchievements.user_id == user_id) &
                    (UsersAchievements.achievement_id == ach.achievement_id)
                ))
            )
            if has_achievement.scalar():
                continue
            upsert_req = (
                insert(UserAchievementProgress)
                .values(
                    user_id=user_id,
                    achievement_id=ach.achievement_id,
                    current_count=1
                )
                .on_conflict_do_update(
                    index_elements=['user_id', 'achievement_id'],
                    set_={
                        'current_count': UserAchievementProgress.current_count + 1
                    }
                )
                .returning(UserAchievementProgress.current_count)
            )
            progress_result = await self.session.execute(upsert_req)
            current_count = progress_result.scalar()
            if current_count >= ach.required_count:
                self.session.add(UsersAchievements(
                    user_id=user_id,
                    achievement_id=ach.achievement_id
                ))
                await self.session.execute(
                    delete(UserAchievementProgress).where(
                        (UserAchievementProgress.user_id==user_id) &
                        (UserAchievementProgress.achievement_id==ach.achievement_id)
                    )
                )
                awarded_achievements.append({
                    "achievement_id": ach.achievement_id,
                    "name": ach.name,
                    "description": ach.description,
                    "icon": ach.icon
                })
        await self.session.commit()
        return awarded_achievements
