import json
from uuid import UUID

from sqlmodel import Session, select

from core.config import get_settings
from core.database import engine
from models.payment import Payment
from models.tenant import Tenant


def _enable_pro(session: Session, slug: str) -> None:
    tenant = session.exec(select(Tenant).where(Tenant.slug == slug)).first()
    assert tenant is not None
    tenant.plan_code = "pro"
    tenant.feature_flags = ["online_payments", "site_sections"]
    session.add(tenant)
    session.commit()


def _shop_with_hold(client, slug: str):
    reg = client.post(
        "/api/onboarding/register",
        json={
            "slug": slug,
            "name": "MP Shop",
            "rubro": "barberia",
            "owner_email": f"owner-{slug}@example.com",
            "owner_password": "securepass123",
        },
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    with Session(engine) as session:
        _enable_pro(session, slug)
    service_id = client.get("/api/admin/catalog/services", headers=headers).json()[0]["id"]
    pro_id = client.post(
        "/api/admin/catalog/professionals",
        headers=headers,
        json={"name": "Ana"},
    ).json()["id"]
    client.post(
        "/api/admin/availability/working-hours",
        headers=headers,
        json={
            "professional_id": pro_id,
            "weekday": 0,
            "start_time": "09:00:00",
            "end_time": "12:00:00",
        },
    )
    slots = client.get(
        f"/api/public/{slug}/slots",
        params={"service_id": service_id, "day": "2026-06-01", "professional_id": pro_id},
    ).json()["slots"]
    book = client.post(
        f"/api/public/{slug}/bookings",
        json={
            "service_id": service_id,
            "professional_id": pro_id,
            "starts_at": slots[0]["starts_at"],
            "customer_name": "Cliente",
            "customer_email": "c@example.com",
        },
    )
    return headers, slug, book.json()["public_code"], book.json()["id"]


def _connect_mp(client, headers):
    auth = client.get("/api/admin/payments/mp/authorize", headers=headers)
    state = auth.json()["url"].split("state=")[-1]
    client.get(
        "/api/admin/payments/mp/callback",
        headers=headers,
        params={"code": "sandbox-code", "state": state},
    )


def test_checkout_stores_platform_fee(client, monkeypatch):
    monkeypatch.setenv("MP_PLATFORM_FEE_PERCENT", "10")
    get_settings.cache_clear()
    headers, slug, public_code, appointment_id = _shop_with_hold(client, "mp-fee")
    _connect_mp(client, headers)
    client.post(f"/api/public/{slug}/bookings/{public_code}/checkout")
    with Session(engine) as session:
        payment = session.exec(
            select(Payment).where(Payment.appointment_id == UUID(appointment_id))
        ).first()
        assert payment is not None
        assert payment.platform_fee_cents > 0


def test_cancel_confirmed_triggers_refund(client):
    headers, slug, public_code, appointment_id = _shop_with_hold(client, "mp-refund")
    _connect_mp(client, headers)
    client.post(f"/api/public/{slug}/bookings/{public_code}/checkout")
    webhook_body = json.dumps(
        {"data": {"id": "pay-refund-1"}, "external_reference": appointment_id}
    ).encode()
    client.post(
        "/api/webhooks/mercadopago/tenant-payments",
        content=webhook_body,
        headers={"x-request-id": "req-refund-1"},
    )
    cancel = client.post(f"/api/public/{slug}/bookings/{public_code}/cancel")
    assert cancel.status_code == 200
    with Session(engine) as session:
        payment = session.exec(
            select(Payment).where(Payment.appointment_id == UUID(appointment_id))
        ).first()
        assert payment is not None
        assert payment.status == "refunded"
