# -*- coding: utf-8 -*-
from typing import Any, Dict

import orjson
import structlog


def censor_password(_, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore
    pw = event_dict.get("password")
    if pw:
        event_dict["password"] = "*CENSORED*"
    return event_dict


structlog.configure(
    cache_logger_on_first_use=True,
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=False),
        censor_password,
        structlog.processors.JSONRenderer(serializer=orjson.dumps),
    ],
    logger_factory=structlog.BytesLoggerFactory(),
)

logger = structlog.get_logger(app="Caishen App")

# TODO: wrap Uvicorn and Gunicorn logging to structlog
