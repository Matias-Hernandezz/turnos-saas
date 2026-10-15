from pydantic import BaseModel, Field


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
