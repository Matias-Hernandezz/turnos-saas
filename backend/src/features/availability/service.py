from uuid import UUID

from sqlmodel import Session

from core.exceptions import NotFoundError
from features.availability.repository import WorkingHoursRepository
from features.availability.schemas import WorkingHoursCreate, WorkingHoursRead, WorkingHoursUpdate
from features.catalog.repository import ProfessionalRepository
from models.availability import WorkingHours
from tenancy.context import TenantContext


class AvailabilityAdminService:
    def __init__(self, session: Session, tenant: TenantContext) -> None:
        self.session = session
        self.tenant = tenant
        self.hours = WorkingHoursRepository(session, tenant.tenant_id)
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
