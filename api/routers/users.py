# -*- coding: utf-8 -*-
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api import crud, models, schemas
from api.dependencies import get_current_user, get_session
from api.settings import settings

prefix = settings.API_VERSION_STR + "/users"
router = APIRouter(prefix=prefix, tags=["User"])


@router.post(
    "/init", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED
)
def create_first_user(
    *, session: Session = Depends(get_session), user_in: schemas.UserCreate
) -> Any:
    user = crud.user.create(session, obj_in=user_in)
    return user


@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    session: Session = Depends(get_session),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new user.
    """
    if crud.user.is_admin(current_user):
        user = crud.user.get_by_email(session, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )
        user = crud.user.create(session, obj_in=user_in)
        # todo: send e-mail
        # if settings.EMAILS_ENABLED and user_in.email:
        #     send_new_account_email(
        #         email_to=user_in.email, username=user_in.email, password=user_in.password
        #     )

        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="You don't have permission to create users.",
    )


@router.put("/", response_model=schemas.UserRead)
def update_user(
    *,
    session: Session = Depends(get_session),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update user.
    """
    if crud.user.is_admin(current_user):
        db_user = crud.user.get(session, id=user_in.id)
        user = crud.user.update(session, db_obj=db_user, obj_in=user_in)
        if user:
            return user
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist."
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="You don't have permission to update users.",
    )


@router.get("/me", response_model=schemas.UserRead)
def read_current_user(
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=schemas.UserRead)
def update_current_user(
    *,
    session: Session = Depends(get_session),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update current user.
    """
    if current_user.is_admin:
        user = crud.user.update(session, db_obj=current_user, obj_in=user_in)
        return user
    user_in = schemas.UserUpdate(
        **user_in.dict(exclude={"is_admin"}, exclude_unset=True)
    )
    user = crud.user.update(session, db_obj=current_user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=schemas.UserRead)
def delete_user(
    *,
    session: Session = Depends(get_session),
    user_id: int,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """Delete a user"""
    if crud.user.is_admin(current_user):
        user = crud.user.get(session, user_id)
        if user:
            return crud.user.delete(session, id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist."
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="You don't have permission to delete users.",
    )


@router.get("/", response_model=List[schemas.UserRead])
def get_multi_users(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """Retrieve a list of users"""
    if crud.user.is_admin(current_user):
        users = crud.user.get_multi(session, skip=offset, limit=limit)
        return users

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="You don't have permission to retrieve users.",
    )
