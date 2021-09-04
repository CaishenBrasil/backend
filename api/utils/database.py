# -*- coding: utf-8 -*-
from settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    connect_args=settings.SQLALCHEMY_CONNECT_ARGS,
    echo=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
