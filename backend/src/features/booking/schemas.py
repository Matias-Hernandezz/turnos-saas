from pydantic import BaseModel, Field


class BookingCreatePublic(BaseModel):
    service_id: str
    professional_id: str | None = None
    starts_at: str
    customer_name: str = Field(min_length=2, max_length=255)
    customer_phone: str | None = Field(default=None, max_length=32)
