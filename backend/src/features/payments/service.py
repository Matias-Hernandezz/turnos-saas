from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session, select

from core.config import get_settings
from core.crypto import CryptoService
from core.exceptions import AppError, NotFoundError
from features.booking.repository import AppointmentRepository
from features.catalog.repository import ServiceRepository
from features.payments.connection_repository import MercadoPagoConnectionRepository
from features.payments.mp_client import MercadoPagoClient
from features.payments.mp_oauth_state import create_mp_oauth_state, parse_mp_oauth_state
from features.payments.repository import PaymentRepository
from models.appointment import Appointment
from models.payment import MercadoPagoConnection, MpWebhookEvent, Payment
from tenancy.context import TenantContext


class PaymentService:
    def __init__(self, session: Session, tenant: TenantContext) -> None:
        self.session = session
        self.tenant = tenant
        self.appointments = AppointmentRepository(session, tenant.tenant_id)
        self.services = ServiceRepository(session, tenant.tenant_id)
        self.payments = PaymentRepository(session, tenant.tenant_id)
        self.connections = MercadoPagoConnectionRepository(session, tenant.tenant_id)
        self.crypto = CryptoService()
        self.mp = MercadoPagoClient()

    def connection_status(self) -> dict:
        conn = self.connections.get_active()
        return {
            "connected": conn is not None,
            "mp_user_id": conn.mp_user_id if conn else None,
        }

    def oauth_authorize_url(self) -> dict:
        if not self.tenant.has_feature("online_payments"):
            raise AppError("Feature not enabled", code="feature")
        state = create_mp_oauth_state(self.tenant.tenant_id)
        settings = get_settings()
        if settings.app_env == "test" or not settings.mp_client_id:
            return {"url": f"https://auth.test/mp?state={state}", "state": state}
        return {"url": self.mp.authorize_url(state), "state": state}

    def oauth_complete(self, code: str, state: str) -> dict:
        tenant_id = parse_mp_oauth_state(state)
        if tenant_id != self.tenant.tenant_id:
            raise AppError("Tenant mismatch", code="oauth_state")
        settings = get_settings()
        if settings.app_env == "test" or not settings.mp_client_id:
            tokens = {
                "access_token": "test-access",
                "refresh_token": "test-refresh",
                "user_id": "test-mp-user",
            }
        else:
            tokens = self.mp.exchange_code(code)
        access = tokens["access_token"]
        refresh = tokens.get("refresh_token") or access
        mp_user_id = str(tokens.get("user_id") or "")
        existing = self.connections.get_active()
        if existing:
            existing.encrypted_access_token = self.crypto.encrypt(access)
            existing.encrypted_refresh_token = self.crypto.encrypt(refresh)
            existing.mp_user_id = mp_user_id or existing.mp_user_id
            existing.is_active = True
            self.session.add(existing)
        else:
            self.session.add(
                MercadoPagoConnection(
                    tenant_id=self.tenant.tenant_id,
                    encrypted_access_token=self.crypto.encrypt(access),
                    encrypted_refresh_token=self.crypto.encrypt(refresh),
                    mp_user_id=mp_user_id or None,
                    is_active=True,
                )
            )
        self.session.commit()
        return {"connected": True, "mp_user_id": mp_user_id or None}

    def _access_token(self) -> str:
        conn = self.connections.get_active()
        if conn is None:
            raise AppError("Mercado Pago not connected", code="mp_not_connected")
        return self.crypto.decrypt(conn.encrypted_access_token)

    def create_deposit_checkout(self, public_code: str) -> dict:
        if not self.tenant.has_feature("online_payments"):
            raise AppError("Payments not available", code="feature")
        row = self.appointments.get_by_public_code(public_code)
        if row is None:
            raise NotFoundError("Appointment not found")
        if row.status != "held":
            raise AppError("Appointment is not awaiting payment", code="invalid_status")
        now = datetime.now(UTC).replace(tzinfo=None)
        if row.hold_expires_at and row.hold_expires_at <= now:
            raise AppError("Hold expired", code="hold_expired")

        service = self.services.get_by_id(row.service_id)
        settings = get_settings()
        amount_cents = max(
            1,
            int(service.price_cents * settings.mp_deposit_percent / 100),
        )

        existing = self.session.exec(
            select(Payment).where(
                Payment.tenant_id == self.tenant.tenant_id,
                Payment.appointment_id == row.id,
                Payment.status == "pending",
            )
        ).first()
        if existing and existing.mp_preference_id:
            return {
                "payment_id": str(existing.id),
                "preference_id": existing.mp_preference_id,
                "init_point": f"https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id={existing.mp_preference_id}",
                "amount_cents": existing.amount_cents,
            }

        access = self._access_token()
        assert row.id is not None
        external_reference = str(row.id)
        notification_url = (
            f"{settings.api_public_base_url.rstrip('/')}/webhooks/mercadopago/tenant-payments"
        )
        back_urls = {
            "success": f"{settings.public_app_base_url}/t/{self.tenant.slug}/reserva/{public_code}",
            "pending": f"{settings.public_app_base_url}/t/{self.tenant.slug}/reserva/{public_code}",
            "failure": f"{settings.public_app_base_url}/t/{self.tenant.slug}/reserva/{public_code}",
        }

        if settings.app_env == "test" or not settings.mp_client_id:
            preference_id = f"test-pref-{row.id}"
            init_point = f"https://sandbox.test/mp/{preference_id}"
        else:
            pref = self.mp.create_preference(
                access,
                title=f"Seña — {service.name}",
                amount_cents=amount_cents,
                external_reference=external_reference,
                notification_url=notification_url,
                back_urls=back_urls,
            )
            preference_id = pref["id"]
            init_point = pref.get("init_point") or pref.get("sandbox_init_point")

        payment = Payment(
            tenant_id=self.tenant.tenant_id,
            appointment_id=row.id,
            mp_preference_id=preference_id,
            amount_cents=amount_cents,
            status="pending",
        )
        self.session.add(payment)
        row.status = "pending_payment"
        self.session.add(row)
        self.session.commit()
        self.session.refresh(payment)
        assert payment.id is not None
        return {
            "payment_id": str(payment.id),
            "preference_id": preference_id,
            "init_point": init_point,
            "amount_cents": amount_cents,
        }

    def apply_payment_notification(
        self,
        *,
        mp_payment_id: str,
        request_id: str,
        payment_data: dict | None = None,
    ) -> bool:
        """Procesa pago aprobado; retorna False si ya procesado (idempotencia)."""
        if self._webhook_seen(request_id):
            return False
        settings = get_settings()
        if payment_data is None:
            access = self._access_token()
            if settings.app_env == "test" or not settings.mp_client_id:
                raise AppError("Missing payment data in test", code="validation")
            payment_data = self.mp.get_payment(access, mp_payment_id)

        status = payment_data.get("status")
        external_ref = payment_data.get("external_reference")
        if not external_ref:
            self._mark_webhook(request_id)
            return True

        appointment_id = UUID(external_ref)
        appointment = self.appointments.get_by_id_optional(appointment_id)
        if appointment is None:
            self._mark_webhook(request_id)
            return True

        payment_row = self.session.exec(
            select(Payment).where(
                Payment.tenant_id == self.tenant.tenant_id,
                Payment.appointment_id == appointment_id,
            )
        ).first()

        if status == "approved":
            if payment_row:
                payment_row.status = "approved"
                payment_row.mp_payment_id = mp_payment_id
                self.session.add(payment_row)
            appointment.status = "confirmed"
            self.session.add(appointment)
        elif payment_row and status in ("rejected", "cancelled"):
            payment_row.status = status
            self.session.add(payment_row)

        self.session.commit()
        self._mark_webhook(request_id)
        return True

    def _webhook_seen(self, request_id: str) -> bool:
        return (
            self.session.exec(
                select(MpWebhookEvent).where(MpWebhookEvent.request_id == request_id)
            ).first()
            is not None
        )

    def _mark_webhook(self, request_id: str) -> None:
        if self._webhook_seen(request_id):
            return
        self.session.add(
            MpWebhookEvent(
                request_id=request_id,
                tenant_id=self.tenant.tenant_id,
            )
        )
        self.session.commit()
