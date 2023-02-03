from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext

from users_fastapi.api.dependencies import get_db_connection
from users_fastapi.db.db import Repo
from users_fastapi.model.auth import Token
from users_fastapi.model.users import UserForm

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    tags=["auth"],
)


def authenticate_user(repo: Repo, email: str, password: str) -> str | None:
    user_auth = repo.get_user_for_auth(email)
    if user_auth and pwd_context.verify(password, user_auth.passhash):
        return user_auth.id
    return None


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload


def user_from_form(form_data: OAuth2PasswordRequestForm = Depends()) -> UserForm:
    # TODO: infer user type from realm
    return UserForm(email=form_data.username, passhash=pwd_context.hash(form_data.password))


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), repo: Repo = Depends(get_db_connection)
):
    user_id = authenticate_user(repo, form_data.username, form_data.password)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user_id}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")
