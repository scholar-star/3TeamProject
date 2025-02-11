from enum import Enum
from fastapi import Depends, HTTPException
from apps.models.author import SignupReq, SigninReq, SigninResp, Dupli_Id
from apps.dependencies.dependencies import get_db_session
from sqlmodel import select, Session
import bcrypt, time
from jose import jwt

class RESULT_CODE(Enum):
    NOT_FOUND = "Not Found"
    FAILED = "Failed"
    SUCCESS = "success"

SECRET_KEY = 'eFgxd67V1cmuXTTq6GuCMBfMWuJiNcYDprvq4'
ALGORITHM = 'HS256'

class AuthService:
    def login_service(self,db:Session, username:str, password:str):
        state = select(SignupReq).where(SignupReq.username == username)
        person = db.exec(state).first()
        if not person:
            raise HTTPException(status_code = 404, detail="User not found")
        
        if (bcrypt.checkpw(password.encode('utf-8'), person.password) and person.username == username):
            payload = {
                "id": person.username,
                "exp": time.time() + 60*30
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
            return SigninResp(token=token, detail=None)
        else:
            raise HTTPException(status_code=401, detail="Login failed")

    def signup_service(self, db:Session, req: SignupReq):
        crypted_password = bcrypt.hashpw(req.password.encode('utf-8'), bcrypt.gensalt())
        req.password = crypted_password
        try:
            db.add(req)
            db.commit() # 트랜잭션
            db.refresh(req)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Failed to create user")
        return {
            "ok":True
        }
    
    def valid_duplicate(self, userId: str, db:Session):
        state = select(SignupReq).where(SignupReq.username == userId)
        person = db.exec(state).first()
        if person:
            return {"ok": False}
        else:
            return {"ok": True}

