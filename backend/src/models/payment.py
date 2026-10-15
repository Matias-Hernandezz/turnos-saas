from uuid import UUID

from sqlmodel import Field, UniqueConstraint

from models.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Payment(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, table=True):
    __tablename__ = "payment"
    __table_args__ = (UniqueConstraint("mp_payment_id", name="uq_payment_mp_id"),)

    appointment_id: UUID = Field(foreign_key="appointment.id", index=True)
    mp_payment_id: str | None = Field(default=None, index=True)
    amount_cents: int
    status: str = Field(default="pending", max_length=32)


class MercadoPagoConnection(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, table=True):
    __tablename__ = "mercado_pago_connection"

    encrypted_refresh_token: str
    mp_user_id: str | None = None
    is_active: bool = True
