import json
from uuid import UUID

from sqlmodel import Session, select

from core.config import get_settings
from core.exceptions import AppError
from features.payments.mp_webhook_verify import verify_mp_signature
from features.payments.service import PaymentService
from models.appointment import Appointment
from tenancy.dependencies import _tenant_context_from_db


def handle_tenant_payment_webhook(
    session: Session,
    *,
    body: bytes,
    x_signature: str | None,
    x_request_id: str | None,
) -> dict:
    settings = get_settings()
    secret = settings.mp_webhook_secret_tenant_payments
    if not secret:
        raise AppError("Webhook not configured", code="webhook_config")

    payload = json.loads(body.decode() or "{}")
    data = payload.get("data") or {}
    data_id = str(data.get("id") or "")
    if not data_id:
        return {"received": True, "ignored": True}

    request_id = x_request_id or f"no-req-{data_id}"
    skip_sig = settings.app_env == "test" and settings.mp_skip_webhook_signature_in_test
    if not skip_sig:
        if not x_signature:
            raise AppError("Missing signature", code="webhook_signature")
        verify_mp_signature(
            secret=secret,
            x_signature=x_signature,
            x_request_id=request_id,
            data_id=data_id,
        )

    # Resolver tenant vía turno (D5): primero necesitamos external_reference del pago.
    # En test, el body puede incluir external_reference para simular.
    external_ref = payload.get("external_reference")
    tenant_id = None
    if external_ref:
        appointment = session.get(Appointment, UUID(external_ref))
        if appointment:
            tenant_id = appointment.tenant_id

    if tenant_id is None:
        # Sin referencia en payload: el servicio obtendrá el pago de MP y resolverá tenant.
        # Requiere al menos un tenant conectado; en MVP usamos el primer match por appointment tras GET.
        return _handle_with_mp_fetch(session, data_id, request_id, secret)

    ctx = _tenant_context_from_db(tenant_id, session)
    svc = PaymentService(session, ctx)
    override = None
    if settings.app_env == "test":
        override = {"status": "approved", "external_reference": external_ref}
    svc.apply_payment_notification(
        mp_payment_id=data_id,
        request_id=request_id,
        payment_data=override,
    )
    return {"received": True}


def _handle_with_mp_fetch(
    session: Session,
    data_id: str,
    request_id: str,
    secret: str,
) -> dict:
    settings = get_settings()
    if settings.app_env == "test":
        return {"received": True, "ignored": True}

    from features.payments.connection_repository import MercadoPagoConnectionRepository
    from models.payment import MercadoPagoConnection
    from features.payments.mp_client import MercadoPagoClient
    from core.crypto import CryptoService

    connections = list(session.exec(select(MercadoPagoConnection).where(MercadoPagoConnection.is_active.is_(True))).all())
    crypto = CryptoService()
    mp = MercadoPagoClient()
    for conn in connections:
        if conn.tenant_id is None:
            continue
        access = crypto.decrypt(conn.encrypted_access_token)
        try:
            payment_data = mp.get_payment(access, data_id)
        except Exception:
            continue
        external_ref = payment_data.get("external_reference")
        if not external_ref:
            continue
        appointment = session.get(Appointment, UUID(external_ref))
        if appointment is None or appointment.tenant_id != conn.tenant_id:
            continue
        ctx = _tenant_context_from_db(conn.tenant_id, session)
        PaymentService(session, ctx).apply_payment_notification(
            mp_payment_id=data_id,
            request_id=request_id,
        )
        return {"received": True}
    return {"received": True, "ignored": True}
