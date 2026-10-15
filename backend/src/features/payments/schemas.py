from pydantic import BaseModel, Field


class PaymentPreferenceCreate(BaseModel):
    appointment_id: str


class MpConnectionStatus(BaseModel):
    connected: bool
    mp_user_id: str | None = None


class MpAuthorizeResponse(BaseModel):
    url: str


class MpOAuthCallbackResponse(BaseModel):
    connected: bool
    mp_user_id: str | None = None


class CheckoutResponse(BaseModel):
    payment_id: str
    preference_id: str
    init_point: str
    amount_cents: int = Field(ge=1)
