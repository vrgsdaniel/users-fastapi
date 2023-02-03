from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class UserAuth(BaseModel):

    id: str
    passhash: str
