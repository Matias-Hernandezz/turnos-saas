from datetime import datetime

from core.config import get_settings
from core.mailer import send_transactional_email


def booking_confirmation_email(
    *,
    to: str,
    tenant_name: str,
    slug: str,
    customer_name: str,
    starts_at: datetime,
    public_code: str,
) -> None:
    settings = get_settings()
    manage_url = f"{settings.public_app_base_url.rstrip('/')}/t/{slug}/reserva/{public_code}"
    when = starts_at.strftime("%d/%m/%Y %H:%M")
    subject = f"Confirmación de turno — {tenant_name}"
    body_text = (
        f"Hola {customer_name},\n\n"
        f"Tu turno en {tenant_name} quedó reservado para el {when}.\n\n"
        f"Para ver el detalle o cancelar, usá este enlace:\n{manage_url}\n\n"
        f"Si no fuiste vos, ignorá este mensaje.\n"
    )
    body_html = (
        f"<p>Hola {customer_name},</p>"
        f"<p>Tu turno en <strong>{tenant_name}</strong> quedó reservado para el "
        f"<strong>{when}</strong>.</p>"
        f'<p><a href="{manage_url}">Ver o cancelar reserva</a></p>'
        f"<p>Si no fuiste vos, ignorá este mensaje.</p>"
    )
    send_transactional_email(to, subject, body_text, body_html)
