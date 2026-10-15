def _setup_with_booking(client, slug: str = "admin-book"):
    reg = client.post(
        "/api/onboarding/register",
        json={
            "slug": slug,
            "name": "Admin Book",
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
    assert book.status_code == 201
    return headers, book.json()["id"], slug


def test_admin_lists_booking_in_week(client):
    headers, appointment_id, slug = _setup_with_booking(client)
    resp = client.get(
        "/api/admin/bookings",
        headers=headers,
        params={"from_date": "2026-06-01", "to_date": "2026-06-07"},
    )
    assert resp.status_code == 200
    ids = [b["id"] for b in resp.json()["bookings"]]
    assert appointment_id in ids


def test_admin_cancel_booking(client):
    headers, appointment_id, _slug = _setup_with_booking(client, slug="admin-cancel")
    patch = client.patch(
        f"/api/admin/bookings/{appointment_id}",
        headers=headers,
        json={"status": "cancelled"},
    )
    assert patch.status_code == 200
    assert patch.json()["status"] == "cancelled"


def test_admin_booking_cross_tenant(client):
    _headers_a, appointment_id, _ = _setup_with_booking(client, slug="shop-ax")
    reg_b = client.post(
        "/api/onboarding/register",
        json={
            "slug": "shop-bx",
            "name": "Shop B",
            "rubro": "barberia",
            "owner_email": "owner-shop-bx@example.com",
            "owner_password": "securepass123",
        },
    )
    assert reg_b.status_code == 200
    token_b = reg_b.json()["access_token"]
    resp = client.get(
        f"/api/admin/bookings/{appointment_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp.status_code == 404
