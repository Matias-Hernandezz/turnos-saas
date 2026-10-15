from pydantic import BaseModel, EmailStr, Field


class BookingCreatePublic(BaseModel):
    service_id: str
    professional_id: str
    starts_at: str
    customer_name: str = Field(min_length=2, max_length=255)
    customer_email: EmailStr | None = None
    customer_phone: str | None = Field(default=None, max_length=32)


class BookingPublicRead(BaseModel):
    id: str
    public_code: str
    status: str
    starts_at: str
    ends_at: str
    hold_expires_at: str
