from datetime import time

from pydantic import BaseModel, Field


class WorkingHoursCreate(BaseModel):
    professional_id: str
    weekday: int = Field(ge=0, le=6)
    start_time: time
    end_time: time


class WorkingHoursRead(BaseModel):
    id: str
    professional_id: str
    weekday: int
    start_time: time
    end_time: time


class WorkingHoursUpdate(BaseModel):
    weekday: int | None = Field(default=None, ge=0, le=6)
    start_time: time | None = None
    end_time: time | None = None
