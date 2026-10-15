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


class SlotRead(BaseModel):
    professional_id: str
    starts_at: str
    ends_at: str


class SlotsResponse(BaseModel):
    day: str
    service_id: str
    slots: list[SlotRead]
