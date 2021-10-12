# -*- coding: utf-8 -*-
from typing import AsyncGenerator

from api.core.database import SessionLocal


async def get_session() -> AsyncGenerator:
    async with SessionLocal() as session:
        yield session
