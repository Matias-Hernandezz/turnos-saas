from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlmodel import Session

from core.exceptions import AppError, NotFoundError
from core.tokens import generate_public_code
from features.availability.slots_service import AvailabilitySlotsService
from features.booking.repository import AppointmentRepository
from features.booking.notifications import booking_confirmation_email
from features.booking.schemas import BookingCreatePublic, BookingPublicRead
from features.catalog.repository import ProfessionalRepository, ServiceRepository
from models.appointment import Appointment
from models.customer import Customer
from models.tenant import Tenant
from tenancy.context import TenantContext


class BookingService:
    HOLD_MINUTES = 15

    def __init__(self, session: Session, tenant: TenantContext) -> None:
        self.session = session
        self.tenant = tenant
        self.appointments = AppointmentRepository(session, tenant.tenant_id)
        self.services = ServiceRepository(session, tenant.tenant_id)
        self.professionals = ProfessionalRepository(session, tenant.tenant_id)

    def create_public_hold(self, body: BookingCreatePublic) -> BookingPublicRead:
        service_id = UUID(body.service_id)
        professional_id = UUID(body.professional_id) if body.professional_id else None
        if professional_id is None:
            raise AppError("professional_id is required", code="validation")

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
        slot_ok = False
        for s in available:
            if s["professional_id"] != str(professional_id):
                continue
            if datetime.fromisoformat(s["starts_at"]) == starts_at:
                slot_ok = True
                break
        if not slot_ok:
            raise AppError("Slot not available", code="slot_unavailable")

        now = datetime.now(UTC).replace(tzinfo=None)
        hold_expires = now + timedelta(minutes=self.HOLD_MINUTES)
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
            status="held",
            public_code=generate_public_code(),
            hold_expires_at=hold_expires,
        )
        self.session.add(appointment)

        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise AppError("Slot not available", code="slot_unavailable")

        self.session.refresh(appointment)
        assert appointment.id is not None

        if body.customer_email:
            tenant_row = self.session.get(Tenant, self.tenant.tenant_id)
            tenant_name = tenant_row.name if tenant_row else self.tenant.slug
            booking_confirmation_email(
                to=str(body.customer_email),
                tenant_name=tenant_name,
                slug=self.tenant.slug,
                customer_name=body.customer_name,
                starts_at=starts_at,
                public_code=appointment.public_code,
            )

        return BookingPublicRead(
            id=str(appointment.id),
            public_code=appointment.public_code,
            status=appointment.status,
            starts_at=appointment.starts_at.isoformat(),
            ends_at=appointment.ends_at.isoformat(),
            hold_expires_at=hold_expires.isoformat(),
        )

    def cancel_by_public_code(self, public_code: str) -> BookingPublicRead:
        row = self.appointments.get_by_public_code(public_code)
        if row is None:
            raise NotFoundError("Booking not found")
        if row.status not in ("held", "confirmed"):
            raise AppError("Booking cannot be cancelled", code="invalid_status")
        row.status = "cancelled"
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        assert row.id is not None
        hold_expires = row.hold_expires_at or row.starts_at
        return BookingPublicRead(
            id=str(row.id),
            public_code=row.public_code,
            status=row.status,
            starts_at=row.starts_at.isoformat(),
            ends_at=row.ends_at.isoformat(),
            hold_expires_at=hold_expires.isoformat(),
        )
