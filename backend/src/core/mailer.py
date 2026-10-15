import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SentEmail:
    to: str
    subject: str
    body_text: str


_outbox: list[SentEmail] = []


def get_email_outbox() -> list[SentEmail]:
    return list(_outbox)


def clear_email_outbox() -> None:
    _outbox.clear()


def send_transactional_email(
    to: str,
    subject: str,
    body_text: str,
    body_html: str | None = None,
) -> None:
    settings = get_settings()
    if settings.app_env == "test":
        _outbox.append(SentEmail(to=to, subject=subject, body_text=body_text))
        return

    if not settings.smtp_host:
        logger.info("email_skipped_no_smtp to=%s subject=%s", to, subject)
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.email_from
    msg["To"] = to
    msg.set_content(body_text)
    if body_html:
        msg.add_alternative(body_html, subtype="html")

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_user and settings.smtp_password:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(msg)
