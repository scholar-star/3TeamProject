import bcrypt
from jose import jwt
import random
from datetime import datetime
from sqlmodel import Session

from apps.dependencies.dependencies import *
from apps.dependencies.tables import *

# 데이터 삽입을 위한 세션 가져오기
def insert_test_data():
    with Session(db_engine) as session:
        # Author(사용자) 데이터 추가
        authors = [
            {"user_id": "testing", "password": "4212", "name": "홍길동", "phone": "010-1234-5678", "email": "test@example.com"},
            {"user_id": "test22", "password": "2222", "name": "김철수", "phone": "010-9876-5432", "email": "test22@example.com"},
        ]

        for author in authors:
            hashed_password = bcrypt.hashpw(author["password"].encode("utf-8"), bcrypt.gensalt())  # 비밀번호 암호화
            new_author = Author(
                user_id=author["user_id"],
                password=hashed_password,
                name=author["name"],
                phone=author["phone"],
                email=author["email"]
            )
            session.add(new_author)

        # Posts(게시글) 데이터 추가
        posts = [
            {"post_id": 1, "user_id": "test", "category": "경제", "title": "경제", "content": "경제내용", "created_at": 1739190448, "published": True},
            {"post_id": 2, "user_id": "testing", "category": "연예", "title": "연예", "content": "내용", "created_at": 1739191191, "published": True},
            {"post_id": 3, "user_id": "testing", "category": "경제", "title": "경제얘기", "content": "돈", "created_at": 1739194362, "published": True},
            {"post_id": 4, "user_id": "testing", "category": "연예", "title": "연예", "content": "뉴스", "created_at": 1739195091, "published": False},
            {"post_id": 5, "user_id": "testing", "category": "패션", "title": "패션", "content": "잡지내용", "created_at": 1739236137, "published": True},
        ]

        # views 값 (1~5 사이 중복 없이 설정)
        views_values = random.sample(range(1, 6), 5)  # 1~5 중복 없이 5개 선택

        for i, post in enumerate(posts):
            new_post = Posts(
                post_id=post["post_id"],
                user_id=post["user_id"],
                category=post["category"],
                title=post["title"],
                content=post["content"],
                created_at=post["created_at"],
                published=post["published"],
                views=views_values[i]  # 중복 없는 views 값 할당
            )
            session.add(new_post)

        # Replys(댓글) 데이터 추가
        replies = [
            {"reply_id": 1, "post_id": 1, "user_id": "testing", "reply": "안녕하세요"},
        ]

        for reply in replies:
            new_reply = Replys(
                reply_id=reply["reply_id"],
                post_id=reply["post_id"],
                user_id=reply["user_id"],
                reply=reply["reply"]
            )
            session.add(new_reply)

        # 최종적으로 커밋하여 데이터 저장
        session.commit()
        print("테스트 데이터 삽입 완료!")

# 데이터베이스 생성 후 테스트 데이터 삽입 실행
if __name__ == "__main__":
    create_db_and_tables()  # 테이블 생성
    insert_test_data()  # 테스트 데이터 삽입
