# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models.base import Base
from .models.user import User  # noqa: F401
from .routers import login, users
from .settings import settings
from .utils.database import engine

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="This API handles User Accounts for the Caishen App",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)

app.include_router(users.router)
app.include_router(login.router)


@app.get("/")
async def root() -> dict:
    return {"message": "Welcome to the Caishen App"}
