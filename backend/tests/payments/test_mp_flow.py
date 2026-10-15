import json

from sqlmodel import Session, select

from core.database import engine
from models.tenant import Tenant


def _enable_pro(session: Session, slug: str) -> None:
    tenant = session.exec(select(Tenant).where(Tenant.slug == slug)).first()
    assert tenant is not None
    tenant.plan_code = "pro"
    tenant.feature_flags = ["online_payments", "site_sections"]
    session.add(tenant)
    session.commit()


def _shop_with_hold(client, slug: str = "mp-shop"):
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
    public_code = book.json()["public_code"]
    appointment_id = book.json()["id"]
    return headers, slug, public_code, appointment_id


def test_mp_oauth_and_checkout_flow(client):
    headers, slug, public_code, appointment_id = _shop_with_hold(client)
    auth = client.get("/api/admin/payments/mp/authorize", headers=headers)
    assert auth.status_code == 200
    state = auth.json()["url"].split("state=")[-1]
    cb = client.get(
        "/api/admin/payments/mp/callback",
        headers=headers,
        params={"code": "sandbox-code", "state": state},
    )
    assert cb.status_code == 200
    assert cb.json()["connected"] is True

    checkout = client.post(f"/api/public/{slug}/bookings/{public_code}/checkout")
    assert checkout.status_code == 200
    assert checkout.json()["init_point"]

    webhook_body = json.dumps(
        {"data": {"id": "pay-123"}, "external_reference": appointment_id}
    ).encode()
    wh = client.post(
        "/api/webhooks/mercadopago/tenant-payments",
        content=webhook_body,
        headers={"x-request-id": "req-1"},
    )
    assert wh.status_code == 200

    get_booking = client.get(f"/api/public/{slug}/bookings/{public_code}")
    assert get_booking.json()["status"] == "confirmed"
