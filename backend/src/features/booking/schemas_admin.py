from pydantic import BaseModel, EmailStr, Field


class BookingAdminRead(BaseModel):
    id: str
    service_id: str
    service_name: str
    professional_id: str | None
    professional_name: str | None
    customer_name: str | None
    customer_phone: str | None
    starts_at: str
    ends_at: str
    status: str
    hold_expires_at: str | None = None


class BookingAdminListResponse(BaseModel):
    from_date: str
    to_date: str
    bookings: list[BookingAdminRead]


class BookingAdminUpdate(BaseModel):
    status: str = Field(description="ej. cancelled, confirmed")


class BookingAdminCreate(BaseModel):
    service_id: str
    professional_id: str
    starts_at: str
    customer_name: str = Field(min_length=2, max_length=255)
    customer_email: EmailStr | None = None
    customer_phone: str | None = Field(default=None, max_length=32)
