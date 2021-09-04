# -*- coding: utf-8 -*-
from typing import Any, Dict, Optional, Union

from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    # General Parameters

    API_VERSION_STR: str = "/api/v1"
    PROJECT_NAME: str = "Caishen App Development Server"

    # DATABASE

    DATABASE_TYPE: str = "sqlite"
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
                scheme="postgresql",
                user=values.get("POSTGRES_USER"),
                password=values.get("POSTGRES_PASSWORD"),
                host=values.get("POSTGRES_SERVER"),
                path=f"/{values.get('POSTGRES_DB') or ''}",
            )
        return "sqlite:///./sql_app.db"

    @validator("SQLALCHEMY_CONNECT_ARGS", pre=True)
    def create_connect_args(cls, values: Dict[str, Any]) -> Dict:
        if values.get("DATABASE_TYPE") == "postgresql":
            return {}
        return {"check_same_thread": False}

    # SECURITY

    SECRET_KEY: str = "MjU0NDJBNDcyRDRCNjE1MDY0NTM2NzU2NkI1OTcwMzM3MzM2NzYzODc5MkY0MjNGNDUyODQ4MkI0RDYyNTE2NQ=="
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 8
    ALGORITHM: str = "HS256"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
