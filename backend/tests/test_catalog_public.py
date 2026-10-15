def test_public_catalog_lists_active_only(client):
    reg = client.post(
        "/api/onboarding/register",
        json={
            "slug": "pub-catalog",
            "name": "Pub",
            "rubro": "barberia",
            "owner_email": "pub@example.com",
            "owner_password": "securepass123",
        },
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    services = client.get("/api/admin/catalog/services", headers=headers).json()
    assert len(services) >= 1

    pro = client.post(
        "/api/admin/catalog/professionals",
        headers=headers,
        json={"name": "Luis"},
    )
    assert pro.status_code == 201

    pub_services = client.get("/api/public/pub-catalog/services").json()
    assert len(pub_services) >= 1
    assert all(s["is_active"] for s in pub_services)

    pub_pros = client.get("/api/public/pub-catalog/professionals").json()
    assert len(pub_pros) == 1
    assert pub_pros[0]["name"] == "Luis"
