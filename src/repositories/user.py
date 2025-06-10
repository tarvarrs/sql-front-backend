from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
from src.models.progress import UserProgress
from src.models.achievement import Achievement, UsersAchievements
from src.models.user import User, PasswordHash


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user_by_login(self, login: str) -> User | None:
        result = await self.session.execute(select(User).where(User.login == login))
        return result.scalars().first()
    
    async def create_user(self, user_data: dict, password: str) -> dict:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(
            login=user_data["login"],
            email=user_data["email"],
            fullname=user_data["fullname"],
            group=user_data["group"],
            total_score=0
        )
        self.session.add(user)
        await self.session.flush()

        password_hash = PasswordHash(user_id=user.user_id, password_hash=hashed_password)
        self.session.add(password_hash)
        user_progress = UserProgress(
            user_id=user.user_id,
            easy_tasks_solved=0,
            medium_tasks_solved=0,
            hard_tasks_solved=0
        )
        self.session.add(user_progress)
        await self.session.commit()
        return user

    async def verify_password(self, login: str, password: str) -> bool:
        user = await self.get_user_by_login(login)
        if not user:
            return False
        result = await self.session.execute(
            select(PasswordHash.password_hash).where(PasswordHash.user_id == user.user_id)
        )
        db_password_hash = result.scalars().first()

        return bcrypt.checkpw(password.encode('utf-8'), db_password_hash.encode('utf-8'))

    async def get_top_users(self, limit: int=10) -> list[dict]:
        achievements_subq = (
            select(
                UsersAchievements.user_id,
                Achievement.icon
            )
            .join(Achievement, Achievement.achievement_id == UsersAchievements.achievement_id)
            .where(Achievement.category_name.like("Техническое мастерство"))
            .subquery()
        )
        user_achievements = (
            select(
                achievements_subq.c.user_id,
                func.array_agg(achievements_subq.c.icon).label("tech_icons")
            )
            .group_by(achievements_subq.c.user_id)
            .subquery()
        )
        result = await self.session.execute(
            select(
                User.user_id,
                User.login,
                User.fullname,
                User.group,
                User.total_score,
                user_achievements.c.tech_icons
            )
            .outerjoin(
                user_achievements,
                user_achievements.c.user_id == User.user_id
            )
            .order_by(User.total_score.desc())
            .limit(limit)
        )
        users = []
        for idx, row in enumerate(result.all(), 1):
            users.append({
                "login": row.login,
                "fullname": row.fullname,
                "group": row.group,
                "total_score": row.total_score,
                "place": idx,
                "achievement_icons": row.tech_icons if row.tech_icons else []
            })
        return users

    async def get_user_place(self, user_id: int) -> dict:
        achievements_subq = (
            select(
                UsersAchievements.user_id,
                Achievement.icon
            )
            .join(Achievement, Achievement.achievement_id == UsersAchievements.achievement_id)
            .where(Achievement.category_name.like("Техническое мастерство"))
            .subquery()
        )
        user_achievements = (
            select(
                achievements_subq.c.user_id,
                func.array_agg(achievements_subq.c.icon).label("tech_icons")
            )
            .group_by(achievements_subq.c.user_id)
            .subquery()
        )
        all_users_query = (
            select(
                User.user_id,
                User.login,
                User.fullname,
                User.group,
                User.total_score,
                user_achievements.c.tech_icons
            )
            .outerjoin(
                user_achievements,
                user_achievements.c.user_id == User.user_id
            )
            .order_by(User.total_score.desc())
        )
        result = await self.session.execute(all_users_query)
        users = result.all()
        user_data = None
        for idx, row in enumerate(users, 1):
            if row.user_id == user_id:
                user_data = {
                    "login": row.login,
                    "fullname": row.fullname,
                    "group": row.group,
                    "total_score": row.total_score,
                    "place": idx,
                    "achievement_icons": row.tech_icons if row.tech_icons else []
                }
                break
        return user_data


    async def get_user_progress_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User)
            .where(User.user_id == user_id)
            )
        return result.scalars().first()
