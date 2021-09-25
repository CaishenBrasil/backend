# -*- coding: utf-8 -*-
from typing import Optional

from fastapi import status

from .base import BaseModel


class BaseLog(BaseModel):
    file_name: str
    class_name: Optional[str]
    function_name: Optional[str]
    event: str
    detail: str


class BaseHTTPRequestLog(BaseLog):
    scheme: str
    method: str
    root_path: str
    path: str


class BaseHTTPResponseLog(BaseHTTPRequestLog):
    status_code: int
    msg: str


class AuthenticationProviderLog(BaseHTTPResponseLog):
    current_provider: Optional[str]
    failed_provider: Optional[str]


class UnAuthorizedUserLog(BaseHTTPResponseLog):
    event: Optional[str] = "Failed to authorize user"
    status_code: Optional[int] = status.HTTP_401_UNAUTHORIZED
