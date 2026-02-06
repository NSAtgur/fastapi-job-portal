from fastapi import Depends, HTTPException,status
from sqlalchemy.orm import Session
from database import get_db, UsersDB
from tokens import verify_token
from fastapi.security import OAuth2PasswordBearer


oauth2schemes = OAuth2PasswordBearer(tokenUrl = '/login')

def login_required(token:str = Depends(oauth2schemes),db: Session = Depends(get_db)):
    payload = verify_token(token)
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Token missing user info")
    user = db.query(UsersDB).filter(UsersDB.email == user_email).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'user not found')
    
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
    return {"skip":skip, "limit":limit}
