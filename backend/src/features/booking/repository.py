from models.appointment import Appointment
from core.base_repository import TenantScopedRepository


class AppointmentRepository(TenantScopedRepository[Appointment]):
    model = Appointment
