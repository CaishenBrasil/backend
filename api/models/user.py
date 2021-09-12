# -*- coding: utf-8 -*-
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, Date, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as _UUID

from .base import Base

if TYPE_CHECKING:
    pass


class User(Base):
    __tablename__ = "users"

    id: UUID = Column(_UUID(as_uuid=True), primary_key=True, default=uuid4)
    birth_date = Column(Date, nullable=False)
    name = Column(String, nullable=False, index=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=True, index=False)
    auth_provider = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
