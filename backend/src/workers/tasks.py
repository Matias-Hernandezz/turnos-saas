from datetime import UTC, datetime

from sqlmodel import Session

from core.database import engine
from features.booking.jobs import expire_expired_holds


def run_expire_holds() -> int:
    now = datetime.now(UTC).replace(tzinfo=None)
    with Session(engine) as session:
        return expire_expired_holds(session, now)
