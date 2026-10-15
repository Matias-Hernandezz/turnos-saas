from datetime import datetime

from sqlmodel import Session, select

from models.appointment import Appointment


def expire_expired_holds(session: Session, now: datetime) -> int:
    """Marca holds vencidos como expired para liberar slots (fase 2)."""
    rows = list(
        session.exec(
            select(Appointment).where(
                Appointment.status == "held",
                Appointment.hold_expires_at.isnot(None),
                Appointment.hold_expires_at <= now,
            )
        ).all()
    )
    for row in rows:
        row.status = "expired"
        session.add(row)
    if rows:
        session.commit()
    return len(rows)
