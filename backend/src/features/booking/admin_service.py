from datetime import UTC, date, datetime, time, timedelta
from uuid import UUID

from sqlmodel import Session

from core.exceptions import AppError, NotFoundError
from core.tokens import generate_public_code
from features.availability.slots_service import AvailabilitySlotsService
from features.booking.repository import AppointmentRepository
from features.booking.schemas_admin import BookingAdminCreate, BookingAdminRead, BookingAdminUpdate
from features.catalog.repository import ProfessionalRepository, ServiceRepository
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
        self.services = ServiceRepository(session, tenant.tenant_id)
        self.professionals = ProfessionalRepository(session, tenant.tenant_id)

    def create_manual(self, body: BookingAdminCreate) -> BookingAdminRead:
        service_id = UUID(body.service_id)
        professional_id = UUID(body.professional_id)
        try:
            starts_at = datetime.fromisoformat(body.starts_at.replace("Z", "+00:00")).replace(
                tzinfo=None
            )
        except ValueError:
            raise AppError("Invalid starts_at", code="validation")

        service = self.services.get_by_id(service_id)
        self.professionals.get_by_id(professional_id)
        ends_at = starts_at + timedelta(minutes=service.duration_minutes)

        slots_svc = AvailabilitySlotsService(self.session, self.tenant.tenant_id)
        day = starts_at.date()
        available = slots_svc.list_slots(
            service_id=service_id,
            day=day,
            professional_id=professional_id,
        )
        slot_ok = any(
            s["professional_id"] == str(professional_id)
            and datetime.fromisoformat(s["starts_at"]) == starts_at
            for s in available
        )
        if not slot_ok:
            raise AppError("Slot not available", code="slot_unavailable")

        now = datetime.now(UTC).replace(tzinfo=None)
        if self.appointments.has_blocking_overlap(
            professional_id=professional_id,
            starts_at=starts_at,
            ends_at=ends_at,
            now=now,
        ):
            raise AppError("Slot not available", code="slot_unavailable")

        customer = Customer(
            tenant_id=self.tenant.tenant_id,
            full_name=body.customer_name,
            email=str(body.customer_email) if body.customer_email else None,
            phone=body.customer_phone,
        )
        self.session.add(customer)
        self.session.flush()

        appointment = Appointment(
            tenant_id=self.tenant.tenant_id,
            service_id=service_id,
            professional_id=professional_id,
            customer_id=customer.id,
            starts_at=starts_at,
            ends_at=ends_at,
            status="confirmed",
            public_code=generate_public_code(),
            hold_expires_at=None,
        )
        self.session.add(appointment)
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise AppError("Slot not available", code="slot_unavailable")
        self.session.refresh(appointment)
        return self._to_read(appointment)

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
