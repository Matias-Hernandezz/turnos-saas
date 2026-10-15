from pydantic import BaseModel, EmailStr, Field


class TenantCreate(BaseModel):
    slug: str = Field(min_length=3, max_length=64, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=2, max_length=255)
    rubro: str = Field(default="barberia", max_length=64)


class RegisterBusinessRequest(BaseModel):
    slug: str = Field(min_length=3, max_length=64, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=2, max_length=255)
    rubro: str = Field(default="barberia", max_length=64)
    owner_email: EmailStr
    owner_password: str = Field(min_length=8, max_length=128)


class TenantRead(BaseModel):
    id: str
    slug: str
    name: str
    plan_code: str
    feature_flags: list[str]
