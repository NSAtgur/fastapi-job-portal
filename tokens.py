from fastapi import Depends, HTTPException, status
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from jose import jwt, JWTError

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM  = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30))



def create_access_token(data:dict):
    to_encode = data.copy()
    exp = datetime.utcnow()+timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp':exp})
    return jwt.encode(to_encode,SECRET_KEY,algorithm = ALGORITHM)


def verify_token(token:str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = " Invalid token")



