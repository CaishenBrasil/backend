# -*- coding: utf-8 -*-
from typing import Any, Dict, Optional

from .base import BaseModel


class BaseLog(BaseModel):
    file_name: str
    class_name: Optional[str]
    function_name: Optional[str]
    event: str
    detail: str


class BaseHTTPRequestLog(BaseLog):
    request: Optional[Dict[str, Any]] = None


class BaseHTTPResponseLog(BaseHTTPRequestLog):
    status_code: int
    msg: str


class AuthenticationProviderLog(BaseHTTPResponseLog):
    current_provider: Optional[str]
    failed_provider: Optional[str]


class UnAuthorizedUserLog(BaseHTTPResponseLog):
    event: Optional[str] = "Failed to authorize user"
