# -*- coding: utf-8 -*-
from .base import CaishenBaseException


class DatabaseException(CaishenBaseException):
    pass


class DatabaseConnectionError(DatabaseException):
    pass


class UnknownDatabaseType(DatabaseException):
    pass
