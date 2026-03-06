from typing import List

from pydantic import BaseModel


class UserRating(BaseModel):
    login: str
    fullname: str | None
    group: str | None
    total_score: int
    place: int
    achievement_icons: List[str] = []

    class Config:
        from_attributes = True


class RatingResponse(BaseModel):
    top_users: list[UserRating]
