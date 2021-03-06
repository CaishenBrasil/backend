# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core import exceptions
from api.core.exceptions.handlers import (
    authentication_provider_error_handler,
    unauthorized_user_handler,
)
from api.core.logging.settings import setup_logging

from .routers import login, users
from .settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="This API handles User Accounts for the Caishen App",
    root_path=settings.ROOT_PATH,
)

# Add Custom Exception Handlers
app.add_exception_handler(
    exceptions.UnAuthorizedUser, handler=unauthorized_user_handler
)

app.add_exception_handler(
    exceptions.AuthenticationProviderMissmatch,
    handler=authentication_provider_error_handler,
)

# Add Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)

# Include Routers
app.include_router(users.router)
app.include_router(login.router)


@app.on_event("startup")
async def init_db() -> None:
    await setup_logging()


@app.get("/")
async def root() -> dict:
    return {"message": "Welcome to the Caishen App"}
