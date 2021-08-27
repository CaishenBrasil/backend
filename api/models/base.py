# -*- coding: utf-8 -*-
from typing import Any

from sqlalchemy.ext.declarative import as_declarative


@as_declarative()
class Base:
    id: Any
