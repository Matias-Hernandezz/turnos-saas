from fastapi import APIRouter, HTTPException, status

from core.config import get_settings

router = APIRouter(prefix="/webhooks/mercadopago", tags=["webhooks"])


@router.post("/subscriptions")
async def mercadopago_subscriptions() -> dict:
    if not get_settings().mp_webhook_secret_subscriptions:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook not configured",
        )
    return {"received": True}
