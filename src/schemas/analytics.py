from pydantic import BaseModel
# from typing import Optional


class TaskThinkingTime(BaseModel):
    task_id: int
    seconds_to_start: float  # Сколько секунд думал
