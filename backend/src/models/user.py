from uuid import UUID

from sqlmodel import Field, SQLModel, UniqueConstraint

from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "user"

    email: str = Field(unique=True, index=True, max_length=320)
    hashed_password: str
    is_active: bool = True


class TenantMembership(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "tenant_membership"
    __table_args__ = (UniqueConstraint("user_id", "tenant_id", name="uq_membership_user_tenant"),)

    user_id: UUID = Field(foreign_key="user.id", index=True)
    tenant_id: UUID = Field(foreign_key="tenant.id", index=True)
    role: str = Field(default="owner", max_length=32)
