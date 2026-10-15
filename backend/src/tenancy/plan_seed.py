from sqlmodel import Session, select

from models.plan import Plan

DEFAULT_PLANS: list[dict] = [
    {
        "code": "basic",
        "name": "Básico",
        "feature_flags": [],
    },
    {
        "code": "pro",
        "name": "Pro",
        "feature_flags": ["online_payments", "site_sections"],
    },
    {
        "code": "max",
        "name": "Max",
        "feature_flags": [
            "online_payments",
            "site_sections",
            "site_builder",
            "custom_domain",
            "whatsapp_reminders",
            "analytics_full",
        ],
    },
]


def ensure_default_plans(session: Session) -> None:
    for item in DEFAULT_PLANS:
        existing = session.exec(select(Plan).where(Plan.code == item["code"])).first()
        if existing is None:
            session.add(
                Plan(
                    code=item["code"],
                    name=item["name"],
                    feature_flags=item["feature_flags"],
                )
            )
    session.commit()


def feature_flags_for_plan_code(session: Session, plan_code: str) -> list[str]:
    plan = session.exec(select(Plan).where(Plan.code == plan_code)).first()
    if plan is None:
        return []
    return list(plan.feature_flags or [])
