from dataclasses import dataclass
from sqlmodel import SQLModel, Field

@dataclass
class SigninReq:
    username: str
    password: str

@dataclass 
class SignupReq:
    username: str
    password: str
    name: str
    phone: str | None = None
    email: str | None = None

@dataclass
class SigninResp:
    token: str
    detail: str | None = None

@dataclass
class Dupli_Id:
    username: str

