from datetime import date, time

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


class TimeOffCreate(BaseModel):
    professional_id: str | None = Field(
        default=None,
        description="Null = bloqueo para todo el negocio",
    )
    start_date: date
    end_date: date
    reason: str | None = Field(default=None, max_length=255)


class TimeOffRead(BaseModel):
    id: str
    professional_id: str | None
    start_date: date
    end_date: date
    reason: str | None


class TimeOffUpdate(BaseModel):
    professional_id: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    reason: str | None = Field(default=None, max_length=255)
