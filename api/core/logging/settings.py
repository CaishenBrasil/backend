# -*- coding: utf-8 -*-
import logging.config
from typing import Any, Dict, Tuple

import structlog
import uvicorn
from pydantic import BaseSettings

from api.core.serializers import orjson_dumps
from api.settings import settings

from .caishen_logger import logger


def censor_password(_, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore
    pw = event_dict.get("password")
    if pw:
        event_dict["password"] = "*CENSORED*"
    return event_dict


shared_processors: Tuple[structlog.types.Processor, ...] = (
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    censor_password,
    structlog.processors.TimeStamper(fmt="iso", utc=False),
)


class LogSettings(BaseSettings):

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
        **uvicorn.config.LOGGING_CONFIG["formatters"],
    }
    handlers: Dict[Any, Any] = {
        "default": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json" if not settings.DEV else "console",
        },
        "uvicorn.access": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "access",
        },
        "uvicorn.default": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    }
    loggers: Dict[Any, Any] = {
        "": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {
            "handlers": ["default" if not settings.DEV else "uvicorn.default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["default" if not settings.DEV else "uvicorn.access"],
            "level": "INFO",
            "propagate": False,
        },
    }


logging_settings = LogSettings()


async def setup_logging() -> None:
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
        wrapper_class=structlog.stdlib.AsyncBoundLogger,
        cache_logger_on_first_use=True,
    )
    logging.config.dictConfig(logging_settings.dict())
    await logger.debug("Finished configuring Logger")
