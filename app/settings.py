from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    database_url: str = Field(pattern=r"^postgresql\+asyncpg://")
    sql_echo: bool = False

    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, le=65535)

    capashino_base_url: str
    capashino_api_key: str
    payment_callback_url: str

    kafka_bootstrap_servers: str
    kafka_order_topic: str
    kafka_shipment_topic: str
    kafka_group_id: str

    kafka_publish_timeout: float = Field(default=10, gt=0)
    outbox_batch_size: int = Field(default=50, ge=1, le=200)
    outbox_poll_interval: float = Field(default=1, gt=0)
    inbox_batch_size: int = Field(default=50, ge=1, le=200)
    inbox_poll_interval: float = Field(default=1, gt=0)
