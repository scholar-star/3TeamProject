from sqlmodel import (
    Field, SQLModel,
    Session, create_engine, select
)

# 테이블을 생성, 클래스 이름이 테이블 이름
class Posts(SQLModel, table=True):
    post_id: int | None = Field(primary_key=True) # primary key로 설정
    user_id: str | None = Field(index=True) 
    category: str = Field(index=True)
    title: str
    content: str
    created_at: int = Field(index=True) # index = True : 인덱스 생성
    published: bool | None
    
    


class PostLike(SQLModel, table=True):
    post_id: int = Field(primary_key=True)
    user_id: str