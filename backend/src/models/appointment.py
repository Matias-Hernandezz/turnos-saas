from datetime import datetime
from uuid import UUID

from sqlmodel import Field, UniqueConstraint

from models.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Appointment(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, table=True):
    __tablename__ = "appointment"
    __table_args__ = (UniqueConstraint("public_code", name="uq_appointment_public_code"),)

    service_id: UUID = Field(foreign_key="service.id")
    professional_id: UUID | None = Field(default=None, foreign_key="professional.id")
    customer_id: UUID | None = Field(default=None, foreign_key="customer.id")
    starts_at: datetime
    ends_at: datetime
    status: str = Field(default="held", max_length=32)
    public_code: str = Field(index=True, max_length=64)
    hold_expires_at: datetime | None = None
