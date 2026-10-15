from datetime import datetime
from uuid import UUID

from sqlmodel import Session, select

from core.base_repository import TenantScopedRepository
from features.booking.overlap import is_blocking_status, ranges_overlap
from models.appointment import Appointment


class AppointmentRepository(TenantScopedRepository[Appointment]):
    model = Appointment

    def list_between(
        self,
        range_start: datetime,
        range_end: datetime,
        professional_id: UUID | None = None,
    ) -> list[Appointment]:
        stmt = select(Appointment).where(
            Appointment.tenant_id == self.tenant_id,
            Appointment.starts_at < range_end,
            Appointment.ends_at > range_start,
        )
        if professional_id is not None:
            stmt = stmt.where(Appointment.professional_id == professional_id)
        stmt = stmt.order_by(Appointment.starts_at)  # type: ignore[arg-type]
        return list(self.session.exec(stmt).all())

    def get_by_public_code(self, public_code: str) -> Appointment | None:
        return self.session.exec(
            select(Appointment).where(
                Appointment.tenant_id == self.tenant_id,
                Appointment.public_code == public_code,
            )
        ).first()

    def has_blocking_overlap(
        self,
        *,
        professional_id: UUID,
        starts_at: datetime,
        ends_at: datetime,
        now: datetime,
        exclude_id: UUID | None = None,
    ) -> bool:
        stmt = select(Appointment).where(
            Appointment.tenant_id == self.tenant_id,
            Appointment.professional_id == professional_id,
        )
        rows = self.session.exec(stmt).all()
        for row in rows:
            if exclude_id is not None and row.id == exclude_id:
                continue
            if not is_blocking_status(row.status, row.hold_expires_at, now):
                continue
            if ranges_overlap(starts_at, ends_at, row.starts_at, row.ends_at):
                return True
        return False

    def list_for_professional_day(
        self,
        professional_id: UUID,
        day_start: datetime,
        day_end: datetime,
        now: datetime,
    ) -> list[Appointment]:
        stmt = select(Appointment).where(
            Appointment.tenant_id == self.tenant_id,
            Appointment.professional_id == professional_id,
            Appointment.starts_at < day_end,
            Appointment.ends_at > day_start,
        )
        rows = list(self.session.exec(stmt).all())
        return [
            r
            for r in rows
            if is_blocking_status(r.status, r.hold_expires_at, now)
        ]
