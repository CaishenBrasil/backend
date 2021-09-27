# -*- coding: utf-8 -*-
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.core.logging.caishen_logger import logger
from api.crud import user
from api.schemas import UserLocalCreate
from api.settings import settings

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    connect_args=settings.SQLALCHEMY_CONNECT_ARGS,
    echo=settings.DEV,
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def create_super_user() -> None:
    username = settings.SUPER_USER_NAME
    password = settings.SUPER_USER_PASSWORD
    email = settings.SUPER_USER_EMAIL
    birthdate = settings.SUPER_USER_BIRTHDATE

    super_user_in = UserLocalCreate(
        name=username,
        password=password,
        email=email,
        birth_date=birthdate,
        is_admin=True,
        auth_provider="LOCAL",
    )

    async with SessionLocal() as session:
        db_super_user = await user.get_by_email(session=session, email=email)
        if db_super_user is None:
            _ = await user.create_local(session=session, obj_in=super_user_in)
            await logger.info("Created SuperUser on DB")
        await logger.info("SuperUser is already created on DB")
    return
