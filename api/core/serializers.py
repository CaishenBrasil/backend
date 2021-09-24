# -*- coding: utf-8 -*-
from typing import Any

import orjson


def orjson_dumps(v: Any, *, default: Any) -> str:
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()
