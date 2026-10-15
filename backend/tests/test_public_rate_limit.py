import os

from core.config import get_settings
from core.rate_limit import reset_rate_limits


def _setup_shop(client, slug: str):
    reg = client.post(
        "/api/onboarding/register",
        json={
            "slug": slug,
            "name": "RL",
            "rubro": "barberia",
            "owner_email": f"rl-{slug}@example.com",
            "owner_password": "securepass123",
        },
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    service_id = client.get("/api/admin/catalog/services", headers=headers).json()[0]["id"]
    pro_id = client.post(
        "/api/admin/catalog/professionals",
        headers=headers,
        json={"name": "P"},
    ).json()["id"]
    return service_id, pro_id


def test_public_slots_rate_limit(client, monkeypatch):
    reset_rate_limits()
    monkeypatch.setenv("PUBLIC_RATE_LIMIT_PER_MINUTE", "2")
    monkeypatch.setenv("PUBLIC_RATE_LIMIT_ENABLED_IN_TEST", "true")
    get_settings.cache_clear()

    service_id, pro_id = _setup_shop(client, "rl-slots")
    params = {"service_id": service_id, "day": "2026-06-01", "professional_id": pro_id}
    assert client.get("/api/public/rl-slots/slots", params=params).status_code == 200
    assert client.get("/api/public/rl-slots/slots", params=params).status_code == 200
    assert client.get("/api/public/rl-slots/slots", params=params).status_code == 429

    get_settings.cache_clear()
