from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel
from dataclasses import dataclass, asdict
from enum import Enum
import time


templates = Jinja2Templates(directory="html")
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