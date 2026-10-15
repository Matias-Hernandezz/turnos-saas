from pydantic import BaseModel, Field


class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    duration_minutes: int = Field(ge=5, le=480)
    price_cents: int = Field(default=0, ge=0)
    is_active: bool = True


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    duration_minutes: int | None = Field(default=None, ge=5, le=480)
    price_cents: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ServiceRead(BaseModel):
    id: str
    name: str
    duration_minutes: int
    price_cents: int
    is_active: bool


class ProfessionalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    is_active: bool = True


class ProfessionalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None


class ProfessionalRead(BaseModel):
    id: str
    name: str
    is_active: bool
