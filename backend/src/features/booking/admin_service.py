from datetime import date, datetime, time, timedelta
from uuid import UUID

from sqlmodel import Session

from core.exceptions import AppError, NotFoundError
from features.booking.repository import AppointmentRepository
from features.booking.schemas_admin import BookingAdminRead, BookingAdminUpdate
from models.appointment import Appointment
from models.catalog import Professional, Service
from models.customer import Customer
from tenancy.context import TenantContext

_CANCELLABLE = frozenset({"held", "confirmed", "pending_payment"})


class BookingAdminService:
    def __init__(self, session: Session, tenant: TenantContext) -> None:
        self.session = session
        self.tenant = tenant
        self.appointments = AppointmentRepository(session, tenant.tenant_id)

    def list_in_range(
        self,
        from_date: date,
        to_date: date,
        professional_id: UUID | None = None,
    ) -> list[BookingAdminRead]:
        if to_date < from_date:
            raise AppError("Invalid date range", code="validation")
        start = datetime.combine(from_date, time.min)
        end = datetime.combine(to_date + timedelta(days=1), time.min)
        rows = self.appointments.list_between(start, end, professional_id)
        return [self._to_read(row) for row in rows]

    def get_by_id(self, appointment_id: UUID) -> BookingAdminRead:
        row = self.appointments.get_by_id_optional(appointment_id)
        if row is None:
            raise NotFoundError("Appointment not found")
        return self._to_read(row)

    def update_status(self, appointment_id: UUID, body: BookingAdminUpdate) -> BookingAdminRead:
        row = self.appointments.get_by_id_optional(appointment_id)
        if row is None:
            raise NotFoundError("Appointment not found")
        new_status = body.status.strip().lower()
        if new_status == "cancelled":
            if row.status not in _CANCELLABLE:
                raise AppError("Appointment cannot be cancelled", code="invalid_status")
            row.status = "cancelled"
        elif new_status == "confirmed":
            if row.status not in ("held", "pending_payment"):
                raise AppError("Appointment cannot be confirmed", code="invalid_status")
            row.status = "confirmed"
        else:
            raise AppError("Unsupported status", code="validation")
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_read(row)

    def _to_read(self, row: Appointment) -> BookingAdminRead:
        assert row.id is not None
        service = self.session.get(Service, row.service_id)
        pro = (
            self.session.get(Professional, row.professional_id)
            if row.professional_id is not None
            else None
        )
        customer = (
            self.session.get(Customer, row.customer_id) if row.customer_id is not None else None
        )
        return BookingAdminRead(
            id=str(row.id),
            service_id=str(row.service_id),
            service_name=service.name if service else "",
            professional_id=str(row.professional_id) if row.professional_id else None,
            professional_name=pro.name if pro else None,
            customer_name=customer.full_name if customer else None,
            customer_phone=customer.phone if customer else None,
            starts_at=row.starts_at.isoformat(),
            ends_at=row.ends_at.isoformat(),
            status=row.status,
            hold_expires_at=row.hold_expires_at.isoformat() if row.hold_expires_at else None,
        )
