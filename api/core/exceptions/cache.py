# -*- coding: utf-8 -*-
from .base import CaishenBaseException


class CacheException(CaishenBaseException):
    pass


class CacheConnectionError(CacheException):
    pass
