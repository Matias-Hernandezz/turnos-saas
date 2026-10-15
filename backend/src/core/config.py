from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_debug: bool = False
    api_prefix: str = "/api"

    database_url: str = "postgresql+psycopg://turnos:turnos@localhost:5432/turnos_saas"

    jwt_secret: str = Field(min_length=16)
    jwt_issuer: str = "turnos-saas"
    jwt_audience: str = "turnos-saas-api"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    fernet_key: str | None = None

    cors_origins: str = "http://localhost:5173"

    trust_proxy_headers: bool = False
    default_public_host: str = "localhost:5173"
    public_app_base_url: str = "http://localhost:5173"
    api_public_base_url: str = "http://localhost:8000/api"

    email_from: str = "noreply@turnos.local"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True

    public_rate_limit_per_minute: int = 60
    public_rate_limit_window_seconds: int = 60
    public_rate_limit_enabled_in_test: bool = False

    mp_webhook_secret_tenant_payments: str | None = None
    mp_webhook_secret_subscriptions: str | None = None
    mp_client_id: str | None = None
    mp_client_secret: str | None = None
    mp_redirect_uri: str = "http://localhost:8000/api/admin/payments/mp/callback"
    mp_deposit_percent: int = 100
    mp_platform_fee_percent: int = 0
    mp_skip_webhook_signature_in_test: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
