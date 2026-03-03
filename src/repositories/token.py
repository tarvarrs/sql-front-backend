from datetime import datetime, timedelta
import secrets
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import UserRefreshToken

class TokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_refresh_token(self, user_id: int) -> str:
        await self.session.execute(
            update(UserRefreshToken)
            .where(UserRefreshToken.user_id == user_id)
            .values(revoked=True)
        )

        token = secrets.token_urlsafe(64)
        expires_at = datetime.now() + timedelta(days=30)
        
        db_token = UserRefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        self.session.add(db_token)
        
        return token

    async def validate_refresh_token(self, token: str) -> Optional[int]:
        result = await self.session.execute(
            select(UserRefreshToken)
            .where(
                (UserRefreshToken.token == token) &
                (UserRefreshToken.expires_at > datetime.now()) &
                (not UserRefreshToken.revoked)
            )
        )
        db_token = result.scalar_one_or_none()
        return db_token.user_id if db_token else None
