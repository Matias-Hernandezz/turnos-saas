"""Cliente HTTP Mercado Pago (OAuth + preferencias + pagos)."""

from typing import Any

import httpx

from core.config import get_settings


class MercadoPagoClient:
    AUTH_BASE = "https://auth.mercadopago.com.ar"
    API_BASE = "https://api.mercadopago.com"

    def authorize_url(self, state: str) -> str:
        settings = get_settings()
        if not settings.mp_client_id:
            raise RuntimeError("MP_CLIENT_ID not configured")
        from urllib.parse import urlencode

        params = urlencode(
            {
                "client_id": settings.mp_client_id,
                "response_type": "code",
                "platform_id": "mp",
                "state": state,
                "redirect_uri": settings.mp_redirect_uri,
            }
        )
        return f"{self.AUTH_BASE}/authorization?{params}"

    def exchange_code(self, code: str) -> dict[str, Any]:
        settings = get_settings()
        if not settings.mp_client_id or not settings.mp_client_secret:
            raise RuntimeError("MP OAuth not configured")
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{self.API_BASE}/oauth/token",
                data={
                    "client_id": settings.mp_client_id,
                    "client_secret": settings.mp_client_secret,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.mp_redirect_uri,
                },
            )
            resp.raise_for_status()
            return resp.json()

    def create_preference(
        self,
        access_token: str,
        *,
        title: str,
        amount_cents: int,
        external_reference: str,
        notification_url: str,
        back_urls: dict[str, str],
    ) -> dict[str, Any]:
        body = {
            "items": [
                {
                    "title": title,
                    "quantity": 1,
                    "unit_price": amount_cents / 100.0,
                    "currency_id": "ARS",
                }
            ],
            "external_reference": external_reference,
            "notification_url": notification_url,
            "back_urls": back_urls,
            "auto_return": "approved",
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{self.API_BASE}/checkout/preferences",
                json=body,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
            return resp.json()

    def get_payment(self, access_token: str, payment_id: str) -> dict[str, Any]:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(
                f"{self.API_BASE}/v1/payments/{payment_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
            return resp.json()
