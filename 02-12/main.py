import sys
sys.path.extend('./')

from apps.dependencies.dependencies import get_db_session, create_db_and_tables
from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import SQLModel, Session, create_engine, select, Field
from dataclasses import dataclass, asdict
from enum import Enum
from apps.models.post import sPostReq, CreatePostReq, PostResp, PostsResp, Posts
from apps.models.author import SigninReq, Dupli_Id, SignupReq
from apps.services.post_service import PostService
from apps.services.reply_service import ReplyService, ReplysResp, ReplyReq
from apps.dependencies.tables import AuthInfo
from apps.services.auth_service import AuthService
from jose import jwt
import time
import bcrypt

SECRET_KEY = 'eFgxd67V1cmuXTTq6GuCMBfMWuJiNcYDprvq4'
ALGORITHM = 'HS256'

templates = Jinja2Templates(directory="front")

app = FastAPI()

login_session = {}

@dataclass
class Token:
    token: str

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/write-post")
def open_write_page(request: Request):
    return templates.TemplateResponse("write_page.html", {"request":request})

@app.post("/write-post")
def create_post(cPost: CreatePostReq):
    nCurTimestamp = int(time.time())
    result = Posts(id=1, title=cPost.title,
                 content=cPost.content,
                 author = cPost.author,
                 created_at=nCurTimestamp,
                 published=cPost.publish)
    print(result)

    return {"ok": True}

@app.post("/login")
def login(req: SigninReq, session=Depends(get_db_session), authService: AuthService = Depends()):
    username = req.username
    password = req.password
    resp = authService.login_service(session, username, password)
    return resp

@app.get("/login")
def viewLogin(req: Request):
    return templates.TemplateResponse("login_page.html", {"request": req})

@app.post("/signup")
def signup(req: SignupReq, session=Depends(get_db_session), authService: AuthService = Depends()):
    resp = authService.signup_service(session, req)
    print(resp)
    return resp

@app.get("/signup")
def viewSignup(req: Request):
    return templates.TemplateResponse("signup_page.html", {"request": req})

@app.post("/duplicate")
def valid_duplicate(req: Dupli_Id, session=Depends(get_db_session), authService: AuthService = Depends()):
    resp = authService.valid_duplicate(req.username, session)
    print(resp)
    return resp

@app.post("/token")
def get_userId(reqToken: Token):
    try:
        payload = jwt.decode(reqToken.token, SECRET_KEY, algorithms=[ALGORITHM]) 
        # {
        # id: user_id
        # exp: expire time
        # }
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/posts")
def get_posts_query(page: int=1, limit: int=2, category: str=None, db=Depends(get_db_session),
                    query: str=None, postService: PostService = Depends()) -> PostsResp:
    resp = postService.get_posts_query(db,page, limit, category, query)
    print(resp)
    return resp

# 홈 페이지에 게시글 목록 불러옴
@app.get("/posts")
def get_posts(page: int=1, limit: int=2, category: str = None,
              db=Depends(get_db_session),
              postService: PostService = Depends()) -> PostsResp:
    resp = postService.get_posts(db, page, limit, category)
    return resp

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

@app.get("/home")
def open_home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request":request})

'''
# 게시글 목록 API (JSON 응답)
@app.get("/posts", response_model=List[Posts])
def get_posts():
    with Session(engine) as session:
        posts = session.exec(select(Posts)).all()
        return posts
'''


# 게시글 조회 페이지 호출
@app.get("/view/{post_id}")
def post_page(request: Request):
    return templates.TemplateResponse("view.html", {"request":request})

# 선택한 게시글 내용 받아옴
@app.post("/view")
def get_post(data: sPostReq, 
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

