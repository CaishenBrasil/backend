# -*- coding: utf-8 -*-
from typing import Optional

from sqlalchemy.engine.result import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import api.models as models
import api.schemas as schemas
from api.core.security import get_password_hash, verify_password

from .base import CRUDBase


class CRUDUser(
    CRUDBase[
        models.User,
        schemas.UserCreate,
        schemas.UserUpdate,
    ]
):
    async def get_by_email(
        self, session: AsyncSession, *, email: str
    ) -> Optional[models.User]:
        result: Result = await session.execute(
            select(models.User).where(models.User.email == email)
        )
        return result.scalars().first()

    async def create(
        self, session: AsyncSession, *, obj_in: schemas.UserCreate
    ) -> models.User:

        db_obj = models.User(
            name=obj_in.name,
            auth_provider=obj_in.auth_provider,
            birth_date=obj_in.birth_date,
            email=obj_in.email,
            is_admin=obj_in.is_admin,
        )
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def create_local(
        self, session: AsyncSession, *, obj_in: schemas.UserLocalCreate
    ) -> models.User:

        db_obj = models.User(
            name=obj_in.name,
            password=get_password_hash(obj_in.password),
            auth_provider=obj_in.auth_provider,
            birth_date=obj_in.birth_date,
            email=obj_in.email,
            is_admin=obj_in.is_admin,
        )
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self, session: AsyncSession, *, db_obj: models.User, obj_in: schemas.UserUpdate
    ) -> models.User:
        if obj_in.password:
            obj_in.password = get_password_hash(obj_in.password)
        return await super().update(session, db_obj=db_obj, obj_in=obj_in)

    async def authenticate(
        self, session: AsyncSession, *, email: str, password: str
    ) -> Optional[models.User]:
        user = await self.get_by_email(session, email=email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def is_admin(self, user: models.User) -> bool:
        return user.is_admin


user = CRUDUser(models.User)
