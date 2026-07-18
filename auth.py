from fastapi import Depends, HTTPException, Query, status
from models import UsersDB
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from tokens import verify_token
from fastapi.security import OAuth2PasswordBearer
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

async def login_required(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = verify_token(token)

    if not isinstance(payload, dict):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token payload')

    user_email = payload.get('sub')
    if not user_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token missing user info')

    result = await db.execute(select(UsersDB).where(UsersDB.email == user_email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User deactivated')

    return user

def role_required(*allowed_roles: str):
    def dependency(user: UsersDB = Depends(login_required)):
        if user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied')
        return user

    return dependency


admin_required = role_required('admin')
recruiter_required = role_required('recruiter')

async def pagination(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    return skip, limit

async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result =await db.execute(select(UsersDB).where(UsersDB.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user
