import logging
import sys

from pydantic import field_validator
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List
from typing import Optional
from typing import Union
from loguru import logger

from app.shared.logging import InterceptHandler


class Config(BaseSettings):

    ### GENERAL ###
    BUILD_ENV: str = None
    DEV: bool = True
    API_V1_STR: str = "/api/v1"
    INVITE_LINK_URL: str = "sotw/invite/"
    SERVER_BIND: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    LOGGER_LEVEL: int = logging.INFO
    LOGGING_CONFIG: str = "/home/clarice/sotw-web-app/app/log_conf.yaml"
    DEBUG: bool = False
    SEND_REGISTRATION_EMAILS: bool = True
    REGISTRATION_VERIFICATION_URL: str = "http://localhost:8080/auth/verify/"
    EMAIL_CHANGE_VERIFICATION_URL: str = "http://localhost:8080/user/email/verify/"
    PASSWORD_RESET_VERIFICATION_URL: str = "http://localhost:8080/password-reset/"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520  # 8 days
    SHARE_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutes
    VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 10  # 10 minutes
    SESSION_COOKIE_EXPIRE_SECONDS: int = 86400  # 30 minutes
    JWT_SECRET: str = (
        "7f0a187153e8c67cd0ef1a27552803e61b0a7051b9d981c8bf41a031b72a74d1"  # use `openssl rand -hex 32` to generate
    )
    ALGORITHM: str = "HS256"

    ### EMAIL ###
    AWS_REGION: str = "us-east-1"
    SMTP_USERNAME: str = "user"
    SMTP_PASSWORD: str = "password"
    SMTP_FROM: str = "songoftheweekaws@gmail.com"  # "no-reply@sotw-app.com"
    SMTP_FROM_NAME: str = "Sotw App"

    ### SPOTIFY ###
    SPOTIFY_CLIENT_ID: str = "id"
    SPOTIFY_CLIENT_SECRET: str = "secret"
    SPOTIFY_CALLBACK_URI: str = "http://localhost/"

    ### MODEL ###
    SOTW_SHARE_ID_K: int = 12

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:8080",
        "http://frontend",
        "http://frontend:8000",
    ]

    BACKEND_CORS_ORIGIN_REGEX: Optional[str] = "http://localhost:8080/*"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")  # 3
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    ### DATABASE ###
    DB_SCHEME: str = "postgresql"
    DB_ASYNC_SCHEME: str = "postgresql+asyncpg"
    DB_HOST: str = "localhost"
    DB_USER: str = "clarice"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "sotw"
    DB_PORT: int = 5432
    DB_CA_PATH: str = "~/.postgresql/root.crt"
    # AWS_ACCESS_KEY_ID: str = "DUMMYIDEXAMPLE"
    # AWS_SECRET_ACCESS_KEY: str = "DUMMYEXAMPLEKEY"
    # AWS_REGION: str = "us-east-1"


def setup_app_logging(config: Config) -> None:
    """Prepare custom logging for our application."""
    LOGGERS = ("uvicorn.asgi", "uvicorn.access")
    logging.getLogger().handlers = [InterceptHandler()]
    for logger_name in LOGGERS:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler(level=config.LOGGER_LEVEL)]

    logger.configure(handlers=[{"sink": sys.stderr, "level": config.LOGGER_LEVEL}])


cfg = Config()
