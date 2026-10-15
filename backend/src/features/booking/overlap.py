from datetime import datetime


def ranges_overlap(start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime) -> bool:
    return start_a < end_b and end_a > start_b


def is_blocking_status(status: str, hold_expires_at: datetime | None, now: datetime) -> bool:
    if status in ("cancelled", "expired"):
        return False
    if status == "held":
        if hold_expires_at is not None and hold_expires_at <= now:
            return False
    return status in ("held", "confirmed", "pending_payment")
