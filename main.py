from fastapi import FastAPI
from dataclasses import dataclass

@dataclass
class SignupReq:
    id: str
    password: str
    Name: str
    Phone: str|None = None
    Email: str

@dataclass
class SigninReq:
    username: str
    password: str

app = FastAPI()

@app.post("/login")
def login(req: SigninReq):
    return {
        "token": "This is token.",
        "detail": None
    }

@app.post("/signup")
def signup(req: SignupReq):
    return {
        "detail": "None"
    }

# DB에서 포스팅 정보를 가지고 온다.
# 단, 포스팅 정보에 주제가 들어가 있다.
