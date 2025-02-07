import sys
sys.path.extend('./')

from apps.dependencies import get_db_session, create_db_and_tables
from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import SQLModel, Session, create_engine, select, Field
from dataclasses import dataclass, asdict
from enum import Enum
import time
import bcrypt

templates = Jinja2Templates(directory="front")

@dataclass
class SignupReq(SQLModel, table=True):
    username: str = Field(primary_key=True)
    password: str
    name: str
    phone: str|None = None
    email: str|None = None

@dataclass
class SigninReq:
    username: str
    password: str

app = FastAPI()

login_session = {}

@dataclass
class Post:
    id: int
    title: str
    content: str
    author: str
    created_at: int
    published: bool

@dataclass
class CreatePostReq:
    title: str
    content: str
    author: str
    publish: bool = True

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/home_page")
def open_home_page(request: Request):
    return templates.TemplateResponse("home_page.html", {"request":request})

@app.get("/write_page")
def open_write_page(request: Request):
    return templates.TemplateResponse("write_page.html", {"request":request})

@app.post("/write_page")
def create_post(cPost: CreatePostReq):
    nCurTimestamp = int(time.time())
    result = Post(id=1, title=cPost.title,
                 content=cPost.content,
                 author = cPost.author,
                 created_at=nCurTimestamp,
                 published=cPost.publish)
    print(result)

    return {"ok": True}

@app.post("/signup_page")
def login(req: SigninReq, session=Depends(get_db_session)):
    state = select(SignupReq).where(SignupReq.username == req.username)
    person = session.exec(state).first()
    if not person:
        raise HTTPException(status_code = 404, detail="User not found")
    
    if bcrypt.checkpw(req.password.encode('utf-8'), person.password):
        return {
            "token": "This is token.",
            "detail": None,
            "ok": True
        }
    else:
        raise HTTPException(status_code=401, detail="Incorrect password")

@app.get("/signup_page")
def viewLogin(req: Request):
    return templates.TemplateResponse("login_page.html", {"request": req})

@app.post("/signup")
def signup(req: SignupReq, session=Depends(get_db_session)):
    crypted_password = bcrypt.hashpw(req.password.encode('utf-8'), bcrypt.gensalt())
    req.password = crypted_password
    print(req)
    try:
        session.add(req)
        session.commit() # 트랜잭션
        session.refresh(req)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to create user")
    return {
        "ok":True
    }

@app.get("/signup")
def viewSignup(req: Request):
    return templates.TemplateResponse("signup_page.html", {"request": req})
 
