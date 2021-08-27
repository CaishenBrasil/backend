# -*- coding: utf-8 -*-
from fastapi import FastAPI

from .models.base import Base
from .models.user import User  # noqa: F401
from .routers import login, users
from .utils.database import engine

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Caishen User API",
    description="This API handles User Accounts for the Caishen App",
)


app.include_router(users.router)
app.include_router(login.router)


@app.get("/")
async def root() -> dict:
    return {"message": "Welcome to the Caishen App"}
