from fastapi import APIRouter, HTTPException, Request, status

from core.config import get_settings

router = APIRouter(prefix="/webhooks/mercadopago", tags=["webhooks"])


@router.post("/tenant-payments")
async def mercadopago_tenant_payments(request: Request) -> dict:
    """Regla D1: verificar firma antes de mutar estado."""
    secret = get_settings().mp_webhook_secret_tenant_payments
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook not configured",
        )
    # TODO: validar x-signature / manifest MP
    _body = await request.body()
    return {"received": True}
