from pydantic import BaseModel, Field


class Mem(BaseModel):
    text: str
    photo: bytes

class Id(BaseModel):
    id: int

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str

class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None

class UserAuth(BaseModel):

    email: str
    password: str