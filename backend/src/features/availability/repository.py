from core.base_repository import TenantScopedRepository
from models.availability import WorkingHours


class WorkingHoursRepository(TenantScopedRepository[WorkingHours]):
    model = WorkingHours
