from pydantic import BaseModel


class UserProgressBase(BaseModel):
    easy_tasks_solved: int
    medium_tasks_solved: int
    hard_tasks_solved: int


class UserProgresCreate(UserProgressBase):
    user_id: int


class UserProgressInDB(UserProgressBase):
    user_id: int

    class Config:
        from_attributes = True
