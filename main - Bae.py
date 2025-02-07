from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import (
    Field, SQLModel,
    Session, create_engine, select
)
from dataclasses import dataclass, asdict
from enum import Enum


from app.services.post_service import *



db_url = 'sqlite:///blog.db'
db_engine = create_engine(db_url,
        connect_args={"check_same_thread": False})



def get_db_session():
    with Session(db_engine) as session:
        yield session

def create_db():
    SQLModel.metadata.create_all(db_engine)


templates = Jinja2Templates(directory="front")
app = FastAPI()
@app.on_event("startup")
def on_startup():
    create_db()




login_session = {}






@app.get("/home")
def open_home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request":request})


@app.get("/posts")
def get_posts(page: int=1, limit: int=2,
              db=Depends(get_db_session),
              postService: PostService = Depends()) -> PostsResp:
    resp = postService.get_posts(db, page, limit)
    return resp

'''
# 게시글 목록 API (JSON 응답)
@app.get("/posts", response_model=List[Posts])
def get_posts():
    with Session(engine) as session:
        posts = session.exec(select(Posts)).all()
        return posts
'''




@app.get("/post")
def open_write_page(request: Request):
    return templates.TemplateResponse("post.html", {"request":request})


@app.post("/post")
def create_post(cPost: PostReq, db = Depends(get_db_session),
                postService: PostService = Depends()):
    resp = postService.create_post(db, cPost)
    print(resp)

    return resp