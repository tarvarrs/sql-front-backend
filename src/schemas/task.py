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

class SQLResponse(BaseModel):
    columns: List[str]
    data: List[List[Any]]
    row_count: int

class SQLRequest(BaseModel):
    sql_query: str

class ValidationResult(BaseModel):
    is_correct: bool
    message: Optional[str] = None

class TaskShortInfo(BaseModel):
    task_id: int
    task_global_id: int
    title: str

class MissionsResponse(BaseModel):
    missions: Dict[int, List[TaskShortInfo]]  # {mission_id: [task1, task2]}

class SolvedTasksResponse(BaseModel):
    solved_missions: Dict[int, List[TaskShortInfo]]  # {mission_id: [task1, task2]}