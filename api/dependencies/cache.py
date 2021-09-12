# -*- coding: utf-8 -*-
from typing import AsyncGenerator

import aioredis

from api.settings import settings


async def get_cache() -> AsyncGenerator:
    redis = aioredis.from_url(settings.REDIS_URI)
    async with redis.client() as cache:
        yield cache
