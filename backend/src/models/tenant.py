from sqlalchemy import Column, JSON
from sqlmodel import Field

from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Tenant(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "tenant"

    slug: str = Field(unique=True, index=True, max_length=64)
    name: str = Field(max_length=255)
    plan_code: str = Field(default="basic", index=True)
    feature_flags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
