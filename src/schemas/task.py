from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class TaskBase(BaseModel):
    mission_id: int
    title: str
    description: str

class TaskCreate(TaskBase):
    clue: str
    correct_query: Optional[str] = None
    expected_result: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class TaskInfo(TaskBase):
    task_global_id: int

    class Config:
        from_attributes = True

class TaskClue(BaseModel):
    clue: str

class TaskExpectedResult(BaseModel):
    expected_result: Dict[str, Any]

class TasksCount(BaseModel):
    easy_tasks_total: int
    medium_tasks_total: int
    hard_tasks_total: int

class TaskSolvedCreate(BaseModel):
    user_id: int
    task_global_id: int