def test_register_business_and_login_flow(client):
    # session fixture ensures tables; client triggers lifespan on first request
    reg = client.post(
        "/api/onboarding/register",
        json={
            "slug": "lauti-barber",
            "name": "Lauti Barber",
            "rubro": "barberia",
            "owner_email": "owner@example.com",
            "owner_password": "securepass123",
        },
    )
    assert reg.status_code == 200
    token = reg.json()["access_token"]

    me = client.get(
        "/api/admin/tenants/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200
    body = me.json()
    assert body["slug"] == "lauti-barber"
    assert body["plan_code"] == "basic"

    services = client.get(
        "/api/admin/catalog/services",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert services.status_code == 200
    assert len(services.json()) >= 1


def test_register_duplicate_slug_conflict(client):
    first = client.post(
        "/api/onboarding/register",
        json={
            "slug": "dup-shop",
            "name": "Dup",
            "rubro": "barberia",
            "owner_email": "dup-a@example.com",
            "owner_password": "securepass123",
        },
    )
    assert first.status_code == 200
    second = client.post(
        "/api/onboarding/register",
        json={
            "slug": "dup-shop",
            "name": "Dup 2",
            "rubro": "barberia",
            "owner_email": "dup-b@example.com",
            "owner_password": "securepass123",
        },
    )
    assert second.status_code == 409
