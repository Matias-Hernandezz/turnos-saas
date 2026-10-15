from sqlmodel import Field

from models.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Review(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, table=True):
    __tablename__ = "review"

    author_name: str = Field(max_length=120)
    body: str = Field(max_length=2000)
    rating: int = Field(ge=1, le=5)
    is_published: bool = False
