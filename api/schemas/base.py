# -*- coding: utf-8 -*-

from pydantic import BaseModel as PydanticBaseModel

from api.core.serializers import orjson, orjson_dumps


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
