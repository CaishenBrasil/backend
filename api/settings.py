# -*- coding: utf-8 -*-
from datetime import date
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator
from pydantic.networks import EmailStr


class Settings(BaseSettings):
    # General Parameters

    API_VERSION_STR: str = "/api/v1"
    PROJECT_NAME: str = "Caishen App Development Server"

    # DATABASE

    DATABASE_TYPE: str = "sqlite"
    DBAPI: Optional[str] = None
    POSTGRES_SERVER: str = None
    POSTGRES_USER: str = None
    POSTGRES_PASSWORD: str = None
    POSTGRES_DB: str = None
    SQLALCHEMY_DATABASE_URI: Optional[Union[PostgresDsn, str]] = None
    SQLALCHEMY_CONNECT_ARGS: Optional[Dict[Any, Any]] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        if values.get("DATABASE_TYPE") == "postgresql":
            return PostgresDsn.build(
                scheme="postgresql+asyncpg",
                user=values.get("POSTGRES_USER"),
                password=values.get("POSTGRES_PASSWORD"),
                host=values.get("POSTGRES_SERVER"),
                path=f"/{values.get('POSTGRES_DB') or ''}",
            )

        return "sqlite+aiosqlite:///./sql_app.db"

    @validator("SQLALCHEMY_CONNECT_ARGS", pre=True)
    def create_connect_args(
        cls, v: Optional[Dict[Any, Any]], values: Dict[str, Any]
    ) -> Dict:
        if isinstance(v, dict):
            return v
        if values.get("DATABASE_TYPE") == "postgresql":
            return {}
        return {"check_same_thread": False}

    # SECURITY

    SECRET_KEY: str = "MjU0NDJBNDcyRDRCNjE1MDY0NTM2NzU2NkI1OTcwMzM3MzM2NzYzODc5MkY0MjNGNDUyODQ4MkI0RDYyNTE2NQ=="
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 8
    ALGORITHM: str = "HS256"

    # CORS

    CORS_ORIGINS: List[AnyHttpUrl] = ["http://www.example.com"]  # type: ignore
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: Union[str, List[str]] = "*"
    ALLOW_HEADERS: Union[str, List[str]] = "*"

    # SUPERUSER
    SUPER_USER_NAME: str = "admin"
    SUPER_USER_PASSWORD: str = "admin"
    SUPER_USER_EMAIL: EmailStr = "admin@example.com"  # type: ignore
    SUPER_USER_BIRTHDATE: date = date(2021, 9, 7)

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
