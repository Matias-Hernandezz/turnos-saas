from core.mailer import clear_email_outbox, get_email_outbox


def _book_one(client, slug: str = "mail-shop", email: str = "cliente@example.com"):
    reg = client.post(
        "/api/onboarding/register",
        json={
            "slug": slug,
            "name": "Mail Shop",
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
    slots = client.get(
        f"/api/public/{slug}/slots",
        params={"service_id": service_id, "day": "2026-06-01", "professional_id": pro_id},
    ).json()["slots"]
    starts_at = slots[0]["starts_at"]
    book = client.post(
        f"/api/public/{slug}/bookings",
        json={
            "service_id": service_id,
            "professional_id": pro_id,
            "starts_at": starts_at,
            "customer_name": "Cliente",
            "customer_email": email,
        },
    )
    return book, slug


def test_booking_sends_confirmation_email(client):
    clear_email_outbox()
    book, slug = _book_one(client)
    assert book.status_code == 201
    public_code = book.json()["public_code"]
    outbox = get_email_outbox()
    assert len(outbox) == 1
    assert outbox[0].to == "cliente@example.com"
    assert public_code in outbox[0].body_text
    assert f"/t/{slug}/reserva/{public_code}" in outbox[0].body_text


def test_cancel_booking_by_public_code(client):
    clear_email_outbox()
    book, slug = _book_one(client, slug="cancel-shop")
    public_code = book.json()["public_code"]
    cancel = client.post(f"/api/public/{slug}/bookings/{public_code}/cancel")
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "cancelled"
    get_resp = client.get(f"/api/public/{slug}/bookings/{public_code}")
    assert get_resp.json()["status"] == "cancelled"
