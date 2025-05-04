from pydantic import BaseModel

class UserRating(BaseModel):
    login: str
    total_score: int
    place: int

    class Config:
        from_attributes = True

class RatingResponse(BaseModel):
    top_users: list[UserRating]
