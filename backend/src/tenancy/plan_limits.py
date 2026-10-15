from tenancy.context import TenantContext


def check_plan_limit(ctx: TenantContext, limit_key: str, current: int, maximum: int | None) -> bool:
    """True si la operación está permitida. maximum None = ilimitado."""
    if maximum is None:
        return True
    return current < maximum


PLAN_LIMITS: dict[str, dict[str, int | None]] = {
    "basic": {"max_professionals": 1},
    "pro": {"max_professionals": 5},
    "max": {"max_professionals": None},
}
