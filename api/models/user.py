# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Date, Integer, String

from .base import Base

# from uuid import UUID, uuid4


# from sqlalchemy.dialects.postgresql import UUID as _UUID


if TYPE_CHECKING:
    pass


class User(Base):
    __tablename__ = "users"

    # id: UUID = Column(_UUID(as_uuid=True), primary_key=True, default=uuid4)
    id = Column(Integer, primary_key=True)
    birth_date = Column(Date, nullable=False)
    name = Column(String, unique=True, nullable=False, index=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, unique=True, nullable=False, index=False)
    is_admin = Column(Boolean, default=False)
