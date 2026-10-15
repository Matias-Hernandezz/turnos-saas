from uuid import UUID

from sqlmodel import Field, UniqueConstraint

from models.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Payment(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, table=True):
    __tablename__ = "payment"
    __table_args__ = (UniqueConstraint("mp_payment_id", name="uq_payment_mp_id"),)

    appointment_id: UUID = Field(foreign_key="appointment.id", index=True)
    mp_preference_id: str | None = Field(default=None, index=True)
    mp_payment_id: str | None = Field(default=None, index=True)
    amount_cents: int
    platform_fee_cents: int = Field(default=0, ge=0)
    status: str = Field(default="pending", max_length=32)


class MpWebhookEvent(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    """Idempotencia de notificaciones MP (regla D1)."""

    __tablename__ = "mp_webhook_event"
    __table_args__ = (UniqueConstraint("request_id", name="uq_mp_webhook_request_id"),)

    request_id: str = Field(index=True, max_length=128)
    tenant_id: UUID | None = Field(default=None, index=True)


class MercadoPagoConnection(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, table=True):
    __tablename__ = "mercado_pago_connection"

    encrypted_access_token: str
    encrypted_refresh_token: str
    mp_user_id: str | None = None
    is_active: bool = True
