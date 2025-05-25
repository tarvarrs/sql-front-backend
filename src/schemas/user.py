from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated


class UserBase(BaseModel):
    login: str
    email: EmailStr
    fullname: str
    group: str


class UserCreate(UserBase):
    password: Annotated [
        str,
        StringConstraints(
            min_length=8
        )
    ]


class UserInDB(UserBase):
    user_id: int
    total_score: int | None = None

    class Config:
        from_attributes = True


class UserPublic(UserBase):
    user_id: int
    total_score: int | None = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    login: str
    password: str
