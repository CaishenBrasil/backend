# -*- coding: utf-8 -*-
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

import api.models as models
import api.schemas as schemas
from api.core.security import get_password_hash, verify_password

from .base import CRUDBase


class CRUDUser(CRUDBase[models.User, schemas.UserCreate, schemas.UserUpdate]):
    def get_by_email(self, session: Session, *, email: str) -> Optional[models.User]:
        return (
            session.execute(select(models.User).where(models.User.email == email))
            .scalars()
            .first()
        )

    def create(self, session: Session, *, obj_in: schemas.UserCreate) -> models.User:

        db_obj = models.User(
            name=obj_in.name,
            password=get_password_hash(obj_in.password),
            birth_date=obj_in.birth_date,
            email=obj_in.email,
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(
        self, session: Session, *, db_obj: models.User, obj_in: schemas.UserUpdate
    ) -> models.User:
        update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            update_data["password"] = hashed_password
        return super().update(session, db_obj=db_obj, obj_in=obj_in)

    # todo: should this be here, or elsewhere?
    def authenticate(
        self, session: Session, *, email: str, password: str
    ) -> Optional[models.User]:
        user = self.get_by_email(session, email=email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def is_admin(self, user: models.User) -> bool:
        return user.is_admin


user = CRUDUser(models.User)
