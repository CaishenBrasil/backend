# -*- coding: utf-8 -*-
from typing import Any

import orjson
from pydantic import BaseModel as PydanticBaseModel


def orjson_dumps(v: Any, *, default: Any) -> str:
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class BaseModel(PydanticBaseModel):
    """
    BaseModel with model Config already initialized with all global parameters defined
    This shall be used when the Schema is not a database model
    """

    class Config:
        anystr_strip_whitespace = True
        validate_assignment = True
        use_enum_values = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class BaseModelORM(PydanticBaseModel):
    """
    BaseModel with model Config already initialized with all global parameters defined
    This shall be used when the Schema is a database model
    """

    class Config:
        orm_mode = True
        anystr_strip_whitespace = True
        validate_assignment = True
        use_enum_values = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps
