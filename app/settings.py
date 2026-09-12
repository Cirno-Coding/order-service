from pathlib import Path
from urllib.parse import quote

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url

    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgres://")

    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgresql://")

    raise ValueError(
        "Database URL must start with postgres://, postgresql:// "
        "or postgresql+asyncpg://"
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Локальный вариант из .env.
    database_url: str = ""

    # Переменные, которые LMS предоставляет по умолчанию.
    postgres_connection_string: str = ""
    postgres_database_name: str = ""
    postgres_host: str = ""
    postgres_port: int = 5432
    postgres_username: str = ""
    postgres_password: str = ""

    sql_echo: bool = False

    api_host: str = "0.0.0.0"
    api_port: int = Field(default=8000, ge=1, le=65535)

    capashino_base_url: str
    capashino_api_key: str
    payment_callback_url: str

    # Эту переменную нужно добавить в LMS.
    kafka_bootstrap_servers: str

    # Значения топиков заданы в условии задания.
    kafka_order_topic: str = "student_system-order.events"
    kafka_shipment_topic: str = "student_system-shipment.events"

    # Если не задана явно, будет уникальна для БД студента.
    kafka_group_id: str = ""

    kafka_publish_timeout: float = Field(default=10, gt=0)
    outbox_batch_size: int = Field(default=50, ge=1, le=200)
    outbox_poll_interval: float = Field(default=1, gt=0)
    inbox_batch_size: int = Field(default=50, ge=1, le=200)
    inbox_poll_interval: float = Field(default=1, gt=0)

    @model_validator(mode="after")
    def configure_database(self) -> "Settings":
        raw_url = self.database_url or self.postgres_connection_string

        if not raw_url:
            required_values = (
                self.postgres_host,
                self.postgres_database_name,
                self.postgres_username,
                self.postgres_password,
            )

            if not all(required_values):
                raise ValueError(
                    "Set DATABASE_URL, POSTGRES_CONNECTION_STRING, "
                    "or complete POSTGRES_* variables"
                )

            username = quote(self.postgres_username, safe="")
            password = quote(self.postgres_password, safe="")
            raw_url = (
                f"postgresql://{username}:{password}"
                f"@{self.postgres_host}:{self.postgres_port}"
                f"/{self.postgres_database_name}"
            )

        self.database_url = normalize_database_url(raw_url)

        if not self.kafka_group_id:
            database_name = (
                self.postgres_database_name
                or "order-service-capashino"
            )
            self.kafka_group_id = f"order-service-{database_name}"

        return self