from datetime import time


def _setup_shop(client):
    reg = client.post(
        "/api/onboarding/register",
        json={
            "slug": "slots-shop",
            "name": "Slots",
            "rubro": "barberia",
            "owner_email": "slots@example.com",
            "owner_password": "securepass123",
        },
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    services = client.get("/api/admin/catalog/services", headers=headers).json()
    service_id = services[0]["id"]

    pro = client.post(
        "/api/admin/catalog/professionals",
        headers=headers,
        json={"name": "Ana"},
    ).json()
    pro_id = pro["id"]

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
    return service_id, pro_id


def test_public_slots_returns_free_windows(client):
    service_id, pro_id = _setup_shop(client)
    # 2026-06-01 is Monday (weekday 0)
    resp = client.get(
        "/api/public/slots-shop/slots",
        params={"service_id": service_id, "day": "2026-06-01", "professional_id": pro_id},
    )
    assert resp.status_code == 200
    slots = resp.json()["slots"]
    assert len(slots) >= 2
    assert slots[0]["starts_at"].startswith("2026-06-01T09:00:00")
