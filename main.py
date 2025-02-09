import sys
sys.path.extend('./')

from apps.dependencies import get_db_session, create_db_and_tables
from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import SQLModel, Session, create_engine, select, Field
from dataclasses import dataclass, asdict
from enum import Enum
from apps.services.post_service import PostService, PostsResp, PostReq, SignupReq, ReplyReq, ReplyService
import time
import bcrypt

templates = Jinja2Templates(directory="front")

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
    return templates.TemplateResponse("home.html", {"request":request})

@app.get("/write-post")
def open_write_page(request: Request):
    return templates.TemplateResponse("write_page.html", {"request":request})

@app.post("/write-post")
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
 
@app.get("/posts/{post_id}/replies")
def open_reply_write(request: Request):
    return templates.TemplateResponse("reply.html", {"request":request})

@app.post("/posts/{post_id}/replies")
def create_reply(rPost: ReplyReq, post_id:int, db = Depends(get_db_session),
                 replyService: ReplyService = Depends()):
    print(post_id)
    rPost.post_id = post_id
    print(rPost)
    resp = replyService.create_reply(db, rPost)
    print(resp)
    return resp

@app.get("/posts/{post_id}/repliesList")
def get_replies(post_id:int, db = Depends(get_db_session),
                replyService: ReplyService = Depends()):
    resp = replyService.get_replys(db, post_id)
    print(resp)
    return resp

@app.put("/posts/{post_id}/replies/{reply_id}")
def update_reply(rPost: ReplyReq, post_id:int, reply_id:int, db = Depends(get_db_session),
                 replyService: ReplyService = Depends()):
    resp = replyService.update_reply(db, reply_id, rPost)
    print(resp)
    return resp

@app.delete("/posts/{post_id}/replies/{reply_id}")
def delete_reply(reply_id:int, db = Depends(get_db_session),
                 replyService: ReplyService = Depends()):
    resp = replyService.delete_reply(db, reply_id)
    print(resp)
    return resp

