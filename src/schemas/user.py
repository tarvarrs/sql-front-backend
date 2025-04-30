from pydantic import BaseModel, EmailStr, StringConstraints, constr
from typing import Annotated

class UserBase(BaseModel):
    login: str
    email: EmailStr

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

# class UserOut(BaseModel):
#     user_id: int
#     login: str
#     email: EmailStr
#     total_score: int

#     class Config:
#         orm_mode = True

# class UserLogin(BaseModel):
#     login: str
#     password: str
