def _shop(client, slug: str):
    reg = client.post(
        "/api/onboarding/register",
        json={
            "slug": slug,
            "name": "Time Off Shop",
            "rubro": "barberia",
            "owner_email": f"owner-{slug}@example.com",
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
    return headers, service_id, pro_id


def test_time_off_blocks_public_slots(client):
    headers, service_id, pro_id = _shop(client, "toff-shop")
    client.post(
        "/api/admin/availability/time-off",
        headers=headers,
        json={
            "professional_id": pro_id,
            "start_date": "2026-06-01",
            "end_date": "2026-06-01",
            "reason": "Feriado",
        },
    )
    resp = client.get(
        "/api/public/toff-shop/slots",
        params={"service_id": service_id, "day": "2026-06-01", "professional_id": pro_id},
    )
    assert resp.status_code == 200
    assert resp.json()["slots"] == []
