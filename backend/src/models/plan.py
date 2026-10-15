from sqlalchemy import Column, JSON
from sqlmodel import Field

from models.mixins import UUIDPrimaryKeyMixin


class Plan(UUIDPrimaryKeyMixin, table=True):
    __tablename__ = "plan"

    code: str = Field(unique=True, index=True)
    name: str
    feature_flags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
