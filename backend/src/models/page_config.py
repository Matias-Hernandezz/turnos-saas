from sqlmodel import Field, JSON, Column

from models.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class PageConfig(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, table=True):
    __tablename__ = "page_config"

    draft_config: dict = Field(default_factory=dict, sa_column=Column(JSON))
    published_config: dict = Field(default_factory=dict, sa_column=Column(JSON))
