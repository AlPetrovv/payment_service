from pathlib import Path

from pydantic import BaseModel, PostgresDsn, AmqpDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent  # src
ROOT_DIR = BASE_DIR.parent  # app
DATA_DIR = ROOT_DIR / "data"
ENV_FILE = ROOT_DIR / ".." / "envs" / "app.env"


class Database(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_pre_ping: bool = True
    pool_size: int = 10
    max_overflow: int = 10

    @property
    def naming_convention(self) -> dict[str, str]:
        return {
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }


class RabbitMQ(BaseModel):
    url: AmqpDsn = Field(default="amqp://guest:guest@rabbitmq:5672/")


class Settings(BaseSettings):
    db: Database
    rabbitmq: RabbitMQ = Field(default_factory=RabbitMQ)
    api_key: str = "secret"
    log_level: str = "INFO"
    version: str = "dev"
    outbox_poll_interval: float = 1.0
    retry_max_attempts: int = 3
    retry_base_delay: float = 2.0
    webhook_timeout: float = 10.0

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="forbid",
        case_sensitive=False,
        env_prefix="APP__",
        env_nested_delimiter="__",
    )


settings = Settings()
