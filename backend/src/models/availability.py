from datetime import date, time
from uuid import UUID

from sqlmodel import Field

from models.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class WorkingHours(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, table=True):
    __tablename__ = "working_hours"

    professional_id: UUID = Field(foreign_key="professional.id", index=True)
    weekday: int = Field(ge=0, le=6)
    start_time: time
    end_time: time


class TimeOff(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, table=True):
    __tablename__ = "time_off"

    professional_id: UUID | None = Field(default=None, foreign_key="professional.id")
    start_date: date
    end_date: date
    reason: str | None = None
