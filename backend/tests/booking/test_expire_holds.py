from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from features.booking.jobs import expire_expired_holds
from models.appointment import Appointment


def test_expire_expired_holds_frees_slot(client):
    reg = client.post(
        "/api/onboarding/register",
        json={
            "slug": "expire-shop",
            "name": "Expire",
            "rubro": "barberia",
            "owner_email": "expire@example.com",
            "owner_password": "securepass123",
        },
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    service_id = client.get("/api/admin/catalog/services", headers=headers).json()[0]["id"]
    pro_id = client.post(
        "/api/admin/catalog/professionals",
        headers=headers,
        json={"name": "Pro"},
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
    starts_at = client.get(
        "/api/public/expire-shop/slots",
        params={"service_id": service_id, "day": "2026-06-01", "professional_id": pro_id},
    ).json()["slots"][0]["starts_at"]

    book = client.post(
        "/api/public/expire-shop/bookings",
        json={
            "service_id": service_id,
            "professional_id": pro_id,
            "starts_at": starts_at,
            "customer_name": "Test",
        },
    )
    assert book.status_code == 201
    public_code = book.json()["public_code"]

    from core.database import engine

    past = datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=1)
    with Session(engine) as session:
        row = session.exec(
            select(Appointment).where(Appointment.public_code == public_code)
        ).first()
        assert row is not None
        row.hold_expires_at = past
        session.add(row)
        session.commit()

    with Session(engine) as session:
        count = expire_expired_holds(session, datetime.now(UTC).replace(tzinfo=None))
        assert count == 1

    slots = client.get(
        "/api/public/expire-shop/slots",
        params={"service_id": service_id, "day": "2026-06-01", "professional_id": pro_id},
    ).json()["slots"]
    assert any(s["starts_at"] == starts_at for s in slots)
