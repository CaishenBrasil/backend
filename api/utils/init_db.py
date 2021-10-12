# -*- coding: utf-8 -*-
import asyncio

from api.core.database import SessionLocal
from api.core.logging.caishen_logger import logger
from api.core.logging.settings import setup_logging
from api.crud.user import user
from api.schemas import UserLocalCreate
from api.settings import settings


async def create_super_user() -> None:

    await setup_logging()

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
        else:
            await logger.info("SuperUser is already created on DB")
    return


def main() -> None:
    asyncio.run(create_super_user())


if __name__ == "__main__":
    main()
