from dataclasses import dataclass
from sqlmodel import SQLModel, Field

@dataclass
class SigninReq:
    username: str
    password: str

@dataclass
class AuthInfo(SQLModel, table=True):
    username: str = Field(primary_key=True)
    password: str
    name: str
    phone: str|None = None
    email: str|None = None

@dataclass
class SigninResp:
    token: str
    detail: str | None = None

@dataclass
class Dupli_Id:
    username: str

