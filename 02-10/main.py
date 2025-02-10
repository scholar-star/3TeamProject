
import sys
sys.path.extend('./')


from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import (
    Field, SQLModel,
    Session, create_engine, select
)
from dataclasses import dataclass, asdict
from enum import Enum


from app.dependencies.dependencies import create_db, get_db_session
from app.services.post_service import *



templates = Jinja2Templates(directory="front")
app = FastAPI()
@app.on_event("startup")
def on_startup():
    create_db()




login_session = {}


# 홈 페이지 html 호출
@app.get("/home")
def open_home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request":request})

# 홈 페이지에 게시글 목록 불러옴
@app.get("/posts")
def get_posts(page: int=1, limit: int=2, category: str = None,
              db=Depends(get_db_session),
              postService: PostService = Depends()) -> PostsResp:
    resp = postService.get_posts(db, page, limit, category)
    return resp

'''
# 게시글 목록 API (JSON 응답)
@app.get("/posts", response_model=List[Posts])
def get_posts():
    with Session(engine) as session:
        posts = session.exec(select(Posts)).all()
        return posts
'''


# 게시글 조회 페이지 호출출
@app.get("/view/{post_id}")
def post_page(request: Request):
    return templates.TemplateResponse("view.html", {"request":request})

# 선택한 게시글 내용 받아옴
@app.post("/view")
def get_post(data: SelectPostReq, 
            db=Depends(get_db_session),
            postService: PostService = Depends()):
    resp = postService.get_post(db, data.post_id)
    return resp

# 게시글 작성 페이지 호출
@app.get("/post")
def open_write_page(request: Request):
    return templates.TemplateResponse("post.html", {"request":request})


# 작성한 게시글 생성 (DB에 저장)
@app.post("/cpost")
def create_post(cPost: CreatePostReq, db = Depends(get_db_session),
                postService: PostService = Depends()):
    resp = postService.create_post(db, cPost)
    print(resp)

    return resp
