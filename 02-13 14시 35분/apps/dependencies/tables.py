from sqlmodel import (
    Field, SQLModel,
    Session, create_engine, select
)



class Author(SQLModel, table=True):
    user_id: str = Field(primary_key=True)
    password: str
    name: str
    phone: str|None = None
    email: str|None = None


# 테이블을 생성, 클래스 이름이 테이블 이름
class Posts(SQLModel, table=True):
    post_id: int | None = Field(primary_key=True) # primary key로 설정
    user_id: str | None = Field(index=True, foreign_key="author.user_id") 
    category: str = Field(index=True)
    title: str
    content: str
    created_at: int = Field(index=True) # index = True : 인덱스 생성
    published: bool | None
    views: int
    
class Replys(SQLModel, table=True):
    reply_id: int | None = Field(primary_key=True)
    post_id: int | None = Field(foreign_key="posts.post_id")
    user_id: str = Field(foreign_key="author.user_id")
    reply: str




