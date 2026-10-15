from core.base_repository import TenantScopedRepository
from models.review import Review


class ReviewRepository(TenantScopedRepository[Review]):
    model = Review
