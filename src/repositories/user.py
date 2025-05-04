from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
from src.models.user import User, PasswordHash

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user_by_login(self, login: str) -> User | None:
        result = await self.session.execute(select(User).where(User.login == login))
        return result.scalars().first()
    
    async def create_user(self, user_data: dict, password: str) -> User:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(
            login=user_data["login"],
            email=user_data["email"],
            total_score=0
        )
        self.session.add(user)
        await self.session.flush()

        password_hash = PasswordHash(user_id=user.user_id, password_hash=hashed_password)
        self.session.add(password_hash)

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
    
    async def get_top_users(self, limit: int=10) -> list[tuple[str, int]]:
        result = await self.session.execute(
            select(
                User.login,
                User.total_score
            )
            .order_by(User.total_score.desc())
            .limit(limit)
        )
        return result.all()
