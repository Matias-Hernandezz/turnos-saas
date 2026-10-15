from datetime import UTC, date, datetime, time, timedelta
from uuid import UUID

from sqlalchemy import or_
from sqlmodel import Session, select

from core.exceptions import NotFoundError
from features.availability.slot_calculator import BusyBlock, generate_slots
from features.catalog.repository import ProfessionalRepository, ServiceRepository
from features.booking.repository import AppointmentRepository
from models.availability import TimeOff, WorkingHours
from models.catalog import Professional


class AvailabilitySlotsService:
    def __init__(self, session: Session, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.services = ServiceRepository(session, tenant_id)
        self.professionals = ProfessionalRepository(session, tenant_id)
        self.appointments = AppointmentRepository(session, tenant_id)

    def list_slots(
        self,
        *,
        service_id: UUID,
        day: date,
        professional_id: UUID | None = None,
    ) -> list[dict]:
        service = self.services.get_by_id(service_id)
        if not service.is_active:
            raise NotFoundError("service")

        now = datetime.now(UTC).replace(tzinfo=None)
        weekday = day.weekday()

        if professional_id is not None:
            pro_ids = [professional_id]
            self.professionals.get_by_id(professional_id)
        else:
            pro_ids = [
                p.id
                for p in self.session.exec(
                    select(Professional).where(
                        Professional.tenant_id == self.tenant_id,
                        Professional.is_active.is_(True),
                    )
                ).all()
                if p.id is not None
            ]

        day_start = datetime.combine(day, time.min)
        day_end = datetime.combine(day, time.max)

        slots: list[dict] = []
        for pro_id in pro_ids:
            if self._is_on_time_off(pro_id, day):
                continue

            windows = self.session.exec(
                select(WorkingHours).where(
                    WorkingHours.tenant_id == self.tenant_id,
                    WorkingHours.professional_id == pro_id,
                    WorkingHours.weekday == weekday,
                )
            ).all()
            if not windows:
                continue

            busy_rows = self.appointments.list_for_professional_day(pro_id, day_start, day_end, now)
            busy = [BusyBlock(start=r.starts_at, end=r.ends_at) for r in busy_rows]

            for window in windows:
                for slot in generate_slots(
                    day=day,
                    open_time=window.start_time,
                    close_time=window.end_time,
                    slot_minutes=service.duration_minutes,
                    busy=busy,
                ):
                    slots.append(
                        {
                            "professional_id": str(pro_id),
                            "starts_at": slot.start.isoformat(),
                            "ends_at": slot.end.isoformat(),
                        }
                    )

        slots.sort(key=lambda s: (s["starts_at"], s["professional_id"]))
        return slots

    def _is_on_time_off(self, professional_id: UUID, day: date) -> bool:
        rows = self.session.exec(
            select(TimeOff).where(
                TimeOff.tenant_id == self.tenant_id,
                or_(
                    TimeOff.professional_id == professional_id,
                    TimeOff.professional_id.is_(None),
                ),
                TimeOff.start_date <= day,
                TimeOff.end_date >= day,
            )
        ).all()
        return len(rows) > 0
