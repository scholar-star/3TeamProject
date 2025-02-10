from dataclasses import asdict
from fastapi import HTTPException
from sqlmodel import (
    Session, select
)
from enum import Enum
import time


from app.dependencies.tables import Posts, PostLike
from app.models.post import *

class RESULT_CODE(Enum):
    NOT_FOUND = "Not Found"
    FAILED = "Failed"
    SUCCESS = "success"





class PostService:
    def get_post(self, db: Session, post_id: int):
        post = db.get(Posts, post_id)

        if not post:
            raise HTTPException(status_code=404, detail="Not Found")

        return {
            "post_id": post.post_id, 
            "user_id": post.user_id, 
            #"category": post.category,
            "title": post.title, 
            "content": post.content, 
            "created_at": post.created_at
        }

    def get_posts(self, db: Session, page: int=1, limit: int=10, category: str=None):
        if page < 1:
            page = 1
        if limit < 1:
            return []
        try:
            nOffset = (page - 1) * limit

            query = select(Posts)
    
            if category and category != "전체":
                query = query.where(Posts.category == category)
            
            posts_query = query.offset(nOffset).limit(limit).order_by(Posts.post_id.desc())
            posts = db.exec(posts_query).all()

            if not posts:
                return PostsResp(posts=[], err_str="해당 페이지에 게시글이 없습니다.")

            return PostsResp(posts=posts)

        except Exception as e:
            return PostsResp(posts=[], err_str=f"서버 오류: {str(e)}")


    def create_post(self, db:Session, cPost: CreatePostReq) -> RESULT_CODE:
        try:
            postModel = Posts()
            postModel.user_id = cPost.user_id
            postModel.category = cPost.category
            postModel.title = cPost.title
            postModel.content = cPost.content
            postModel.created_at = int(time.time())
            postModel.published = cPost.published
            db.add(postModel)
            db.commit()
            db.refresh(postModel)
        except Exception as e:
            print(e)
            return RESULT_CODE.FAILED
        return RESULT_CODE.SUCCESS

    def update_post(self, db:Session, 
                    post_id: int, post: CreatePostReq) -> RESULT_CODE:
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