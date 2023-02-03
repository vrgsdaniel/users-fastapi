from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError

from users_fastapi.api.auth import decode_token, oauth2_scheme, user_from_form
from users_fastapi.api.dependencies import get_db_connection
from users_fastapi.db.db import DuplicateEntryException, Repo
from users_fastapi.model.users import User, UserForm, Users, UserUpdate

router = APIRouter(tags=["users"])


async def get_current_user(token: str = Depends(oauth2_scheme), repo: Repo = Depends(get_db_connection)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = repo.get_user_by_field("id", user_id)
    if user is None:
        raise credentials_exception
    return user


@router.get(
    "/users/me",
    response_model=User,
    status_code=status.HTTP_200_OK,
)
def read_current_user(
    user: User = Depends(get_current_user),
):
    return user


@router.get(
    "/users/all",
    response_model=Users,
    status_code=status.HTTP_200_OK,
)
def list_all_users(
    skip: int = 0,
    limit: int = 10,
    user: User = Depends(get_current_user),
    repo: Repo = Depends(get_db_connection),
):
    if not user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Operation not allowerd",
        )
    users = repo.list_users(limit, skip)
    return users


@router.post(
    "/users",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_create: UserForm = Depends(user_from_form),
    repo: Repo = Depends(get_db_connection),
):
    try:
        user = repo.create_user(user_create)
    except DuplicateEntryException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    return user


@router.put(
    "/users",
    response_model=User,
    status_code=status.HTTP_200_OK,
)
def update_user(
    update_user: UserUpdate,
    user: User = Depends(get_current_user),
    repo: Repo = Depends(get_db_connection),
):
    try:
        user = repo.update_user(user.id, update_user.value, update_user.field)
    except DuplicateEntryException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )

    return user


@router.delete(
    "/users",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user: User = Depends(get_current_user),
    repo: Repo = Depends(get_db_connection),
):
    repo.delete_user(user.id)
