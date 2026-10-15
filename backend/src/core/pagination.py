from pydantic import BaseModel, Field


class PageParams(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)


class PageMeta(BaseModel):
    offset: int
    limit: int
    total: int | None = None
