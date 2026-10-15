from sqlmodel import Field

from models.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Service(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, table=True):
    __tablename__ = "service"

    name: str = Field(max_length=255)
    duration_minutes: int = Field(ge=5, le=480)
    price_cents: int = Field(default=0, ge=0)
    is_active: bool = True


class Professional(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, table=True):
    __tablename__ = "professional"

    name: str = Field(max_length=255)
    is_active: bool = True
