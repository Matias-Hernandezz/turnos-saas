from datetime import time


def _setup_booking_shop(client):
    reg = client.post(
        "/api/onboarding/register",
        json={
            "slug": "book-shop",
            "name": "Book",
            "rubro": "barberia",
            "owner_email": "book@example.com",
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
    slots = client.get(
        "/api/public/book-shop/slots",
        params={"service_id": service_id, "day": "2026-06-01", "professional_id": pro_id},
    ).json()["slots"]
    assert slots
    return service_id, pro_id, slots[0]["starts_at"]


def test_second_booking_same_slot_conflicts(client):
    service_id, pro_id, starts_at = _setup_booking_shop(client)
    payload = {
        "service_id": service_id,
        "professional_id": pro_id,
        "starts_at": starts_at,
        "customer_name": "Cliente Uno",
        "customer_phone": "+541100000001",
    }
    first = client.post("/api/public/book-shop/bookings", json=payload)
    assert first.status_code == 201

    payload["customer_name"] = "Cliente Dos"
    payload["customer_phone"] = "+541100000002"
    second = client.post("/api/public/book-shop/bookings", json=payload)
    assert second.status_code == 409
