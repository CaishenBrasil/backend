# -*- coding: utf-8 -*-
from typing import Dict

from fastapi import APIRouter

from api.settings import settings

prefix = settings.API_VERSION_STR + "/login"
router = APIRouter(prefix=prefix, tags=["Login"])


@router.get("/")
def login() -> Dict:
    return {"message": "This is supposed to be the login endpoint"}


@router.get("/google-login", tags=["Social Login"], description="Google Oauth Login")
def google_login() -> Dict:
    return {"message": "This is supposed to be the Google login endpoint"}


@router.get(
    "/facebook-login", tags=["Social Login"], description="Facebook Oauth Login"
)
def facebook_login() -> Dict:
    return {"message": "This is supposed to be the Facebook login endpoint"}
