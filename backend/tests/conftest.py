import os

os.environ.setdefault("JWT_SECRET", "test-jwt-secret-key-32chars-min")
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("FERNET_KEY", "52__lssIZJzbQEORyYVtc-ne4vFYFGAZyDgs0rvD3-U=")
os.environ.setdefault("MP_WEBHOOK_SECRET_TENANT_PAYMENTS", "test-webhook-secret")

from core.config import get_settings

get_settings.cache_clear()

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

import models  # noqa: F401
from core.database import engine, init_db
from main import app
from tenancy.plan_seed import ensure_default_plans


@pytest.fixture(scope="session", autouse=True)
def _db_schema():
    init_db()
    with Session(engine) as session:
        ensure_default_plans(session)
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(name="session")
def session_fixture():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
