from dataclasses import dataclass, asdict
from sqlmodel import (
    Field, SQLModel,
    Session, create_engine, select, Relationship
)
from enum import Enum
import time

class RESULT_CODE(Enum):
    NOT_FOUND = "Not Found"
    FAILED = "Failed"
    SUCCESS = "success"

@dataclass
class SignupReq(SQLModel, table=True):
    username: str = Field(primary_key=True)
    password: str
    name: str
    phone: str|None = None
    email: str|None = None

# 테이블을 생성, 클래스 이름이 테이블 이름
class Posts(SQLModel, table=True):
    post_id: int | None = Field(primary_key=True) # primary key로 설정
    user_id: int | None = Field(index=True) 
    created_at: int | None = Field(index=True) # index = True : 인덱스 생성
    title: str
    content: str
    published: bool = Field(index=True)

@dataclass
class PostReq:
    user_id: str
    title: str
    content: str
    published: bool = True

@dataclass
class PostsResp:
    posts: list[Posts]
    err_str: str | None = None

@dataclass # 댓글 데이터베이스 - user_id는 외래키
class Replys(SQLModel, table=True):
    reply_id: int | None = Field(primary_key=True)
    post_id: int | None = Field(foreign_key="posts.post_id")
    user_id: str = Field(foreign_key="signupreq.username")
    reply: str

@dataclass
class ReplyReq:
    user_id: str
    reply: str

@dataclass
class ReplysResp:
    replys: list[Replys]
    err_str: str | None = None

class PostService:
    def get_post(self, db: Session, post_id: int):
        pass

    def get_posts(self, db: Session, page: int=1, limit: int=10):
        '''if page < 1:
            page = 1
        if limit < 1:
            return []
        
        nOffset = (page-1) * limit

        posts = db.exec(
            select(Posts).offset(nOffset).limit(limit)
        ).all()

        posts = PostsResp(posts=posts)
        return posts'''
        if page < 1:
            page = 1
        if limit < 1:
            return []
        try:
            nOffset = (page - 1) * limit
            posts_query = select(Posts).offset(nOffset).limit(limit)
            posts = db.exec(posts_query).all()

            if not posts:
                return PostsResp(posts=[], err_str="해당 페이지에 게시글이 없습니다.")

            return PostsResp(posts=posts)

        except Exception as e:
            return PostsResp(posts=[], err_str=f"서버 오류: {str(e)}")


    def create_post(self, db:Session, cPost: PostReq) -> RESULT_CODE:
        try:
            postModel = Posts()
            postModel.user_id = cPost.user_id
            postModel.title = cPost.title
            postModel.content = cPost.content
            postModel.created_at = int(time.time())
            postModel.published = cPost.published
            db.add(postModel)
            db.commit()
            db.refresh(postModel)
        except:
            return RESULT_CODE.FAILED
        return RESULT_CODE.SUCCESS

    def update_post(self, db:Session, 
                    post_id: int, post: PostReq) -> RESULT_CODE:
        oldPost = db.get(Posts, post_id)
        if not oldPost:
            return (None, RESULT_CODE.NOT_FOUND)
        
        dictToUpdate = asdict(post)
        oldPost.sqlmodel_update(dictToUpdate)
        try:
            db.add(oldPost)
            db.commit()
            db.refresh(oldPost)
        except:
            return (None, RESULT_CODE.FAILED)
        return (oldPost, RESULT_CODE.SUCCESS)
    

    def delete_post(self, db: Session, post_id: int) -> RESULT_CODE:
        post = db.get(Posts, post_id)
        if not post:
            return RESULT_CODE.NOT_FOUND
        try:
            db.delete(post)
            db.commit()
        except:
            return RESULT_CODE.FAILED
        return RESULT_CODE.SUCCESS
    
class ReplyService:
    def get_replys(self, db: Session, post_id: int):
        replys_query = select(Replys).where(Replys.post_id == post_id)
        try:
            replys = db.exec(replys_query).all()
            if not replys:
                return ReplysResp(replys=[])
            return ReplysResp(replys=replys)
        except Exception as e:
            print(e)
            return ReplysResp(replys=[], err_str="서버 오류")
        

    def create_reply(self, db:Session, rPost: ReplyReq) -> RESULT_CODE:
        try:
            reply = Replys()
            reply.post_id = rPost.post_id
            reply.user_id = rPost.user_id
            reply.reply = rPost.reply
            db.add(reply)
            db.commit()
            db.refresh(reply)
        except Exception as e:
            print(e)
            return RESULT_CODE.FAILED

    def update_reply(self, db:Session, reply_id: int, reply: ReplyReq) -> RESULT_CODE:
        oldReply = db.get(Replys, reply_id)
        if not oldReply:
            return RESULT_CODE.NOT_FOUND

        dictReply = asdict(reply) # dataclass를 dictionary로 변환
        oldReply.sqlmodel_update(dictReply) # 딕셔너리 상태로 업데이트
        try:
            db.add(oldReply)
            db.commit()
            db.refresh(oldReply)
        except:
            return RESULT_CODE.FAILED

    def delete_reply(self, db: Session, reply_id: int) -> RESULT_CODE:
        deleteReply = db.get(Replys, reply_id)
        if not deleteReply:
            return RESULT_CODE.NOT_FOUND
        
        try:
            db.delete(deleteReply)
            db.commit()
        except:
            return RESULT_CODE.FAILED

