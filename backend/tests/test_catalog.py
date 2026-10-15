def _register(client, slug: str, email: str) -> str:
    r = client.post(
        "/api/onboarding/register",
        json={
            "slug": slug,
            "name": slug,
            "rubro": "barberia",
            "owner_email": email,
            "owner_password": "securepass123",
        },
    )
    assert r.status_code == 200
    return r.json()["access_token"]


def test_professional_plan_limit_basic(client):
    token = _register(client, "shop-a", "a@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    first = client.post(
        "/api/admin/catalog/professionals",
        headers=headers,
        json={"name": "Pro 1"},
    )
    assert first.status_code == 201

    second = client.post(
        "/api/admin/catalog/professionals",
        headers=headers,
        json={"name": "Pro 2"},
    )
    assert second.status_code == 403


def test_cross_tenant_service_not_visible(client):
    token_a = _register(client, "tenant-a", "ta@example.com")
    token_b = _register(client, "tenant-b", "tb@example.com")

    created = client.post(
        "/api/admin/catalog/services",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"name": "Secret cut", "duration_minutes": 30, "price_cents": 100},
    )
    assert created.status_code == 201
    service_id = created.json()["id"]

    listed_b = client.get(
        "/api/admin/catalog/services",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    ids_b = {s["id"] for s in listed_b.json()}
    assert service_id not in ids_b

    patch_b = client.patch(
        f"/api/admin/catalog/services/{service_id}",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"name": "Hacked"},
    )
    assert patch_b.status_code == 404
