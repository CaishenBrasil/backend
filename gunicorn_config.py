# -*- coding: utf-8 -*-
import logging.config
import multiprocessing
import os
from ipaddress import IPv4Address
from typing import Any, Dict, Optional

import structlog
from pydantic import BaseSettings, validator

from api.core.logging.settings import shared_processors
from api.core.serializers import orjson_dumps
from api.settings import settings


class GunicornSettings(BaseSettings):
    WORKERS_PER_CORE: float = 1.0
    MAX_WORKERS: Optional[int] = None
    HOST: Optional[IPv4Address] = None

    @validator("HOST", pre=True)
    def define_default_host(
        cls, v: Optional[IPv4Address], values: Dict[str, Any]
    ) -> IPv4Address:
        if v is None:
            return IPv4Address("0.0.0.0")
        else:
            return v

    PORT: int = 80
    BIND: Optional[str] = None

    @validator("BIND", pre=True)
    def define_bind(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if v is None:
            host = values.get("HOST")
            port = values.get("PORT")
            return f"{host}:{port}"
        else:
            return v

    LOG_LEVEL: str = "INFO"
    CORES: int = multiprocessing.cpu_count()
    WEB_CONCURRENCY: Optional[int] = None

    @validator("WEB_CONCURRENCY", pre=True)
    def define_web_concurrency_value(
        cls, v: Optional[int], values: Dict[str, Any]
    ) -> int:
        default_web_concurrency = values.get("WORKERS_PER_CORE") * values.get("CORES")
        if v is None:
            return default_web_concurrency
        else:
            web_concurrency = max(default_web_concurrency, 2)
            if values.get("MAX_WORKERS"):
                web_concurrency = min(web_concurrency, values.get("MAX_WORKERS"))
            return web_concurrency

    ACCESS_LOG: str = "-"
    ERROR_LOG: str = "-"
    GRACEFUL_TIMEOUT: int = 120
    TIMEOUT: int = 120
    KEEP_ALIVE: int = 5

    class Config:
        case_sensitive = True
        env_file = "gunicorn.env"
        env_file_encoding = "utf-8"


gunicorn_conf = GunicornSettings()

# Gunicorn config variables
loglevel = gunicorn_conf.LOG_LEVEL
workers = gunicorn_conf.WEB_CONCURRENCY
bind = gunicorn_conf.BIND
errorlog = gunicorn_conf.ERROR_LOG
worker_tmp_dir = "/dev/shm"
accesslog = gunicorn_conf.ACCESS_LOG
graceful_timeout = gunicorn_conf.GRACEFUL_TIMEOUT
timeout = gunicorn_conf.TIMEOUT
keepalive = gunicorn_conf.KEEP_ALIVE


class GunicornLogSettings(BaseSettings):
    version: int = 1
    disable_existing_loggers: bool = False

    formatters: Dict[Any, Any] = {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(serializer=orjson_dumps),
            "foreign_pre_chain": shared_processors,
        },
        "console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
            "foreign_pre_chain": shared_processors,
        },
    }

    handlers: Dict[Any, Any] = {
        "development": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
        "production": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    }

    loggers: Dict[Any, Any] = {
        "": {
            "handlers": ["development" if settings.DEV else "production"],
            "level": gunicorn_conf.LOG_LEVEL,
            "propagate": True,
        },
    }


logging.config.dictConfig(GunicornLogSettings().dict())


structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        *shared_processors,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


class GunicornLogger:
    """
    Gunicorn Logger class to use structlog instead of default logging library
    """

    def __init__(self, cfg: Any) -> None:
        self.error_log = structlog.get_logger("gunicorn.error")
        self.error_log.setLevel(gunicorn_conf.LOG_LEVEL)
        self.access_log = structlog.get_logger("gunicorn.access")
        self.access_log.setLevel(gunicorn_conf.LOG_LEVEL)
        self.cfg = cfg
        self._gunicorn_config()

    def critical(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self.error_log.error(msg, *args, **kwargs)

    def error(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self.error_log.error(msg, *args, **kwargs)

    def warning(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self.error_log.warning(msg, *args, **kwargs)

    def info(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self.error_log.info(msg, *args, **kwargs)

    def debug(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self.error_log.debug(msg, *args, **kwargs)

    def exception(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self.error_log.exception(msg, *args, **kwargs)

    def log(self, lvl: str, msg: Any, *args: Any, **kwargs: Any) -> None:
        self.error_log.log(lvl, msg, *args, **kwargs)

    def access(self, resp: Any, req: Any, environ: dict, request_time: Any) -> None:
        status = resp.status
        if isinstance(status, str):
            status = status.split(None, 1)[0]

        self.access_log.info(
            "request",
            method=environ["REQUEST_METHOD"],
            request_uri=environ["RAW_URI"],
            status=status,
            response_length=getattr(resp, "sent", None),
            request_time_seconds="%d.%06d"
            % (request_time.seconds, request_time.microseconds),
            pid="<%s>" % os.getpid(),
        )

    def reopen_files(self) -> None:
        pass  # we don't support files

    def close_on_exec(self) -> None:
        pass  # we don't support files

    def _gunicorn_config(self) -> None:
        """
        Log Gunicorn Configuration used to start Gunicorn service
        """
        self.info(gunicorn_conf.json())
