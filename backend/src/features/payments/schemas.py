from pydantic import BaseModel


class PaymentPreferenceCreate(BaseModel):
    appointment_id: str
