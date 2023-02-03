from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel


class UserField(str, Enum):
    email = "email"


class UserType(str, Enum):
    admin = "ADMIN"
    customer = "CUSTOMER"


class TokenData(BaseModel):
    user_id: str | None


class User(BaseModel):
    """Representation of User entity"""

    id: str = uuid4()
    email: str
    user_type: UserType
    created_at: datetime | None

    def is_admin(self):
        return self.user_type == UserType.admin


class Users(BaseModel):
    users: list[User]


class UserUpdate(BaseModel):

    field: UserField
    value: str


class UserForm(BaseModel):
    email: str
    passhash: str
    user_type: UserType = UserType.customer
