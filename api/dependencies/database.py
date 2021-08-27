# -*- coding: utf-8 -*-
from typing import Generator

from api.utils.database import SessionLocal


def get_session() -> Generator:
    with SessionLocal() as session:
        yield session
