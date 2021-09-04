# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.settings import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    connect_args=settings.SQLALCHEMY_CONNECT_ARGS,
    echo=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
