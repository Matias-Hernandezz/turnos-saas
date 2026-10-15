from uuid import UUID

from sqlmodel import Session

from core.exceptions import NotFoundError
from features.availability.repository import WorkingHoursRepository
from features.availability.schemas import (
    TimeOffCreate,
    TimeOffRead,
    TimeOffUpdate,
    WorkingHoursCreate,
    WorkingHoursRead,
    WorkingHoursUpdate,
)
from features.availability.time_off_repository import TimeOffRepository
from features.catalog.repository import ProfessionalRepository
from models.availability import TimeOff, WorkingHours
from tenancy.context import TenantContext


class AvailabilityAdminService:
    def __init__(self, session: Session, tenant: TenantContext) -> None:
        self.session = session
        self.tenant = tenant
        self.hours = WorkingHoursRepository(session, tenant.tenant_id)
        self.time_off = TimeOffRepository(session, tenant.tenant_id)
        self.professionals = ProfessionalRepository(session, tenant.tenant_id)

    def list_working_hours(self, professional_id: UUID | None = None) -> list[WorkingHoursRead]:
        rows = self.hours.list_all(limit=500)
        if professional_id is not None:
            rows = [r for r in rows if r.professional_id == professional_id]
        return [self._read(r) for r in rows]

    def create_working_hours(self, body: WorkingHoursCreate) -> WorkingHoursRead:
        pro_id = UUID(body.professional_id)
        self.professionals.get_by_id(pro_id)
        if body.end_time <= body.start_time:
            raise ValueError("end_time must be after start_time")
        entity = WorkingHours(
            tenant_id=self.tenant.tenant_id,
            professional_id=pro_id,
            weekday=body.weekday,
            start_time=body.start_time,
            end_time=body.end_time,
        )
        saved = self.hours.add(entity)
        self.session.commit()
        self.session.refresh(saved)
        return self._read(saved)

    def update_working_hours(self, hours_id: UUID, body: WorkingHoursUpdate) -> WorkingHoursRead:
        entity = self.hours.get_by_id(hours_id)
        if body.weekday is not None:
            entity.weekday = body.weekday
        if body.start_time is not None:
            entity.start_time = body.start_time
        if body.end_time is not None:
            entity.end_time = body.end_time
        if entity.end_time <= entity.start_time:
            raise ValueError("end_time must be after start_time")
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return self._read(entity)

    def delete_working_hours(self, hours_id: UUID) -> None:
        entity = self.hours.get_by_id(hours_id)
        self.session.delete(entity)
        self.session.commit()

    def list_time_off(self, professional_id: UUID | None = None) -> list[TimeOffRead]:
        rows = self.time_off.list_all(limit=500)
        if professional_id is not None:
            rows = [
                r
                for r in rows
                if r.professional_id == professional_id or r.professional_id is None
            ]
        return [self._time_off_read(r) for r in rows]

    def create_time_off(self, body: TimeOffCreate) -> TimeOffRead:
        if body.end_date < body.start_date:
            raise ValueError("end_date must be on or after start_date")
        pro_id: UUID | None = None
        if body.professional_id:
            pro_id = UUID(body.professional_id)
            self.professionals.get_by_id(pro_id)
        entity = TimeOff(
            tenant_id=self.tenant.tenant_id,
            professional_id=pro_id,
            start_date=body.start_date,
            end_date=body.end_date,
            reason=body.reason,
        )
        saved = self.time_off.add(entity)
        self.session.commit()
        self.session.refresh(saved)
        return self._time_off_read(saved)

    def update_time_off(self, time_off_id: UUID, body: TimeOffUpdate) -> TimeOffRead:
        entity = self.time_off.get_by_id(time_off_id)
        if body.professional_id is not None:
            if body.professional_id == "":
                entity.professional_id = None
            else:
                pro_id = UUID(body.professional_id)
                self.professionals.get_by_id(pro_id)
                entity.professional_id = pro_id
        if body.start_date is not None:
            entity.start_date = body.start_date
        if body.end_date is not None:
            entity.end_date = body.end_date
        if body.reason is not None:
            entity.reason = body.reason
        if entity.end_date < entity.start_date:
            raise ValueError("end_date must be on or after start_date")
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return self._time_off_read(entity)

    def delete_time_off(self, time_off_id: UUID) -> None:
        entity = self.time_off.get_by_id(time_off_id)
        self.session.delete(entity)
        self.session.commit()

    @staticmethod
    def _time_off_read(row: TimeOff) -> TimeOffRead:
        assert row.id is not None
        return TimeOffRead(
            id=str(row.id),
            professional_id=str(row.professional_id) if row.professional_id else None,
            start_date=row.start_date,
            end_date=row.end_date,
            reason=row.reason,
        )

    @staticmethod
    def _read(row: WorkingHours) -> WorkingHoursRead:
        assert row.id is not None
        return WorkingHoursRead(
            id=str(row.id),
            professional_id=str(row.professional_id),
            weekday=row.weekday,
            start_time=row.start_time,
            end_time=row.end_time,
        )
