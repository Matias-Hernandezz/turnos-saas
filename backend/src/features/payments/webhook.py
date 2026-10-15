from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session

from core.config import get_settings
from core.database import get_session
from core.exceptions import AppError
from features.payments.webhook_handler import handle_tenant_payment_webhook

router = APIRouter(prefix="/webhooks/mercadopago", tags=["webhooks"])


@router.post("/tenant-payments")
async def mercadopago_tenant_payments(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
) -> dict:
    """Regla D1: verificar firma antes de mutar estado."""
    settings = get_settings()
    if not settings.mp_webhook_secret_tenant_payments:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook not configured",
        )
    body = await request.body()
    try:
        return handle_tenant_payment_webhook(
            session,
            body=body,
            x_signature=request.headers.get("x-signature"),
            x_request_id=request.headers.get("x-request-id"),
        )
    except AppError as exc:
        if exc.code in ("webhook_signature", "webhook_config"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
