from fastapi import Depends, HTTPException, status, APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, BackgroundTasks
from database import UsersDB, ApplicationsDB, JobsDB, NotificationsDB, get_db
from fastapi.security import OAuth2PasswordRequestForm
from tokens import create_access_token, verify_token
from security import verify_password_hash, generate_password_hash
from iotype import CreateUser, UserResponse, JobCreate, JobResponse, ApplicationResponse, NotificationResponse, UploadResponse
from sqlalchemy.orm import Session
from auth import login_required, admin_required, recruiter_required, pagination
from typing import List
from ws_manager import manager
from sqlalchemy import or_
from dotenv import load_dotenv
import os
from worker import process_notification
from PIL import Image
import cloudinary
import cloudinary.uploader
from pydantic import BaseModel, CongfigDict
import logging

router = APIRouter()
load_dotenv()

tasks = []

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

logger = logging.getLogger(__name__)



@router.post('/register', response_model=UserResponse)
def register_user(
            user: CreateUser,
            db: Session = Depends(get_db
            )):
    
    existing_user = db.query(UsersDB).filter(UsersDB.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered")
    try:
        hashed_password = generate_password_hash(user.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    new_user = UsersDB(name=user.name, email=user.email, password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info("User %s registered", new_user.name)
    return new_user


@router.post('/login')
def login_user(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
        ):
    user = db.query(UsersDB).filter(UsersDB.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User deactivated")

    if not verify_password_hash(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Password")

    access_token = create_access_token({"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post('/postjob', response_model=JobResponse)
def post_job(
        job: JobCreate,
        background_tasks: BackgroundTasks, 
        r: UsersDB = Depends(recruiter_required), 
        db: Session = Depends(get_db)
        ):
    
    new_job = JobsDB(title=job.title, company=job.company, salary=job.salary, location=job.location, job_type=job.job_type, created_by=r.id)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    logger.info("User %s posted new job", r.name, new_job.title)

    users = db.query(UsersDB).filter(UsersDB.role == "user", UsersDB.is_active == True).all()
    user_ids = [user.id for user in users]

    background_tasks.add_task(process_notification, {
        "receiver_id": user_ids,
        "type": "job posted",
        "job_id": new_job.id
    })

    return new_job


@router.get('/search', response_model=List[JobResponse])
def search_job(
    title: str, 
    p=Depends(pagination), 
    db: Session = Depends(get_db)
    ):
    skip, limit = p
    jobs = db.query(JobsDB).filter(or_(JobsDB.title.ilike(f"%{title}%"))).offset(skip).limit(limit).all()
    return jobs


@router.post('/apply/{job_id}', response_model=ApplicationResponse)
def apply(job_id: int, background_tasks: BackgroundTasks, user: UsersDB = Depends(login_required), db: Session = Depends(get_db)):
    job = db.query(JobsDB).filter(JobsDB.id == job_id).first()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    existing_application = db.query(ApplicationsDB).filter(ApplicationsDB.user_id == user.id, ApplicationsDB.job_id == job_id).first()
    if existing_application:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already applied")

    new_application = ApplicationsDB(user_name=user.name,user_id=user.id, job_id=job_id, status="applied")
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    
    logger.info(f"{user.name} applied for {job.title}")
    background_tasks.add_task(process_notification, {
        "receiver_id": job.created_by,
        "type": "application",
        "user_id": user.id,
        "job_id": job_id
    })

    return new_application


@router.get('/profile/user', response_model=UserResponse)
def user_profile(user: UsersDB = Depends(login_required)):
    return user


@router.get('/profile/user/applications', response_model=List[ApplicationResponse])
def user_applications(user: UsersDB = Depends(login_required), p=Depends(pagination), db: Session = Depends(get_db)):
    skip, limit = p
    applications = db.query(ApplicationsDB).filter(ApplicationsDB.user_id == user.id).offset(skip).limit(limit).all()
    return applications


@router.get('/profile/recruiter', response_model=UserResponse)
def recruiter_profile(recruiter: UsersDB = Depends(recruiter_required)):
    return recruiter


@router.get('/profile/admin', response_model=UserResponse)
def admin_profile(user: UsersDB = Depends(admin_required)):
    return user


@router.get('/profile/recruiter/posts', response_model=List[JobResponse])
def recruiter_posts(recruiter: UsersDB = Depends(recruiter_required), p=Depends(pagination), db: Session = Depends(get_db)):
    skip, limit = p
    posts = db.query(JobsDB).filter(JobsDB.created_by == recruiter.id).offset(skip).limit(limit).all()
    return posts


@router.delete('/profile/recruiter/posts/delete', response_model=JobResponse)
def delete_jobposts(job_id: int, background_tasks: BackgroundTasks, recruiter: UsersDB = Depends(recruiter_required), db: Session = Depends(get_db)):
    job = db.query(JobsDB).filter(JobsDB.id == job_id, JobsDB.created_by == recruiter.id).first()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    # save details before deleting
    job_title = job.title
    job_company = job.company

    db.delete(job)
    db.commit()

    logger.info("User %s deleted the job posting", recruiter.name, job.title)

    background_tasks.add_task(process_notification, {
        "receiver_id": recruiter.id,
        "type": "job deleted",
        "job_title": job_title,
        "job_company": job_company
    })

    return job


@router.get('/admin/users', response_model=List[UserResponse])
def get_users(admin: UsersDB = Depends(admin_required), p=Depends(pagination), db: Session = Depends(get_db)):
    skip, limit = p
    users = db.query(UsersDB).offset(skip).limit(limit).all()
    return users


@router.patch('/admin/user/deactivate', response_model=UserResponse)
def deactivate_user(user_id: int, background_tasks: BackgroundTasks, admin: UsersDB = Depends(admin_required), db: Session = Depends(get_db)):
    user = db.query(UsersDB).filter(UsersDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = False
    db.commit()

    logger.info("Admin deactivated user %s", user.name)

    background_tasks.add_task(process_notification, {
        "receiver_id": user_id,
        "type": "deactivated"
    })

    return user


@router.patch('/admin/user/activate', response_model=UserResponse)
def activate_user(user_id: int, background_tasks: BackgroundTasks, admin: UsersDB = Depends(admin_required), db: Session = Depends(get_db)):
    user = db.query(UsersDB).filter(UsersDB.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already active")

    user.is_active = True
    db.commit()
    db.refresh(user)
    
    logger.info("User %s activated successful", user.name)

    background_tasks.add_task(process_notification, {
        "receiver_id": user_id,
        "type": "activated"
    })

    return user


@router.get('/admin/user', response_model=UserResponse)
def get_user(user_id: int, admin: UsersDB = Depends(admin_required), db: Session = Depends(get_db)):
    user = db.query(UsersDB).filter(UsersDB.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    return user


@router.get('/admin/promote-admin', response_model=UserResponse)
def promote_user(user_id: int, admin: UsersDB = Depends(admin_required), db: Session = Depends(get_db)):
    user = db.query(UsersDB).filter(UsersDB.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.get('/profile/notifications', response_model=List[NotificationResponse])
def notifications(user=Depends(login_required), p=Depends(pagination), db: Session = Depends(get_db)):
    skip, limit = p
    notifications = db.query(NotificationsDB).filter(NotificationsDB.user_id == user.id).order_by(NotificationsDB.id.desc()).offset(skip).limit(limit).all()
    return notifications


@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    payload = verify_token(token)
    useremail = payload.get("sub")

    if not useremail:
        await websocket.close(code=1008)
        return

    user = db.query(UsersDB).filter(UsersDB.email == useremail).first()

    if not user:
        await websocket.close(code=1008)
        return

    await manager.connect(user.id, websocket)
    
    try:
        while True:
            await websocket.receive_text()
            logger.info("Message is sent")
    except WebSocketDisconnect:
        logger.exception("WS error")
        manager.disconnect(user.id)


@router.post('/profile/upload', response_model=UploadResponse)
async def upload_pic(file: UploadFile = File(...), user=Depends(login_required), db: Session = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only images allowed")

    try:
        image = Image.open(file.file)
        image.verify()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only images allowed")

    file.file.seek(0)

    if user.profile_pic_public_id:
        try:
            cloudinary.uploader.destroy(user.profile_pic_public_id)
        except Exception:
            pass

    result = cloudinary.uploader.upload(file.file)
    image_url = result.get("secure_url")
    public_id = result.get("public_id")

    user.profile_pic = image_url
    user.profile_pic_public_id = public_id
    db.commit()
    db.refresh(user)
    logger.info("Profile pic uploaded")
    return {"image_url": image_url}

class UserInfo(BaseModel):
    id:int
    name:str
    email:str

@router.post('/users',response_model=UserInfo)
def get_userinfo(name:str, email:str, db:Session = Depends(get_db)):
    user = db.query(UsersDB).filter(UsersDB.name==name and UsersDB.email==email).first()
    if not user:
        new_user= UsersDB(name=name, email=email)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    