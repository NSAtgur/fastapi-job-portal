from fastapi import Depends, HTTPException,status
from sqlalchemy.orm import Session
from database import get_db, UsersDB
from tokens import verify_token
from fastapi.security import OAuth2PasswordBearer
import json
from config import QUEUE_NAME
from redis_client import redis_conn


oauth2schemes = OAuth2PasswordBearer(tokenUrl = '/login')

def login_required(token:str = Depends(oauth2schemes),db: Session = Depends(get_db)):
    payload = verify_token(token)
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Token missing user info")
    user = db.query(UsersDB).filter(UsersDB.email == user_email).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'user not found')
    if not user.is_active:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="User deactivated")
    return user


def admin_required(user:UsersDB = Depends(login_required)):
    if user.role != 'admin':
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = " Access denied!")
    return user


def recruiter_required(user: UsersDB = Depends(login_required)):
    if user.role != 'recruiter':
        raise HTTPException( status_code = status.HTTP_403_FORBIDDEN, detail = " Access denied ")
    return user


def pagination( skip:int = 0, limit:int = 10):
    return skip,limit

def get_user(user_id:int, db:Session=Depends(get_db)):
    user= db.query(UsersDB).filter(UsersDB.id == user_id).first()
    return user

def push_notifications(data:dict):
    redis_conn.lpush(QUEUE_NAME,json.dumps(data))
    