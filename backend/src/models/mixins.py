from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class UUIDPrimaryKeyMixin(SQLModel):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TenantScopedMixin(SQLModel):
    tenant_id: UUID = Field(index=True, foreign_key="tenant.id")
