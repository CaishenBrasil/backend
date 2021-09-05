# -*- coding: utf-8 -*-
from fastapi import FastAPI

from .models import Base, User  # noqa: F401
from .routers import login, users
from .utils.database import engine

app = FastAPI(
    title="Caishen User API",
    description="This API handles User Accounts for the Caishen App",
)


app.include_router(users.router)
app.include_router(login.router)


@app.on_event("startup")
async def db_init() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root() -> dict:
    return {"message": "Welcome to the Caishen App"}
