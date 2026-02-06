from fastapi import Depends, HTTPException, status, APIRouter, WebSocket, WebSocketDisconnect
from database import UsersDB,ApplicationsDB, JobsDB, get_db
from fastapi.security import OAuth2PasswordRequestForm
from tokens import create_access_token, verify_token
from security import verify_password_hash, generate_password_hash
from iotype import CreateUser, UserResponse, JobCreate, JobResponse, JobApply, ApplicationResponse
from sqlalchemy.orm import Session
from auth import login_required, admin_required, recruiter_required, pagination
from typing import List
from ws_manager import ConnectionManager, manager

router = APIRouter()

@router.post('/register', response_model = UserResponse)
def register_user(user: CreateUser, db: Session = Depends(get_db)):
    existing_user = db.query(UsersDB).filter(UsersDB.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = " User already registered")
    try:
        hashed_password = generate_password_hash(user.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    new_user = UsersDB( email = user.email, password = hashed_password, role = user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post('/login')
def login_user(form_data: OAuth2PasswordRequestForm= Depends(), db: Session = Depends(get_db)):
    user = db.query(UsersDB).filter(UsersDB.email == form_data.username).first()
    if not user or not verify_password_hash(form_data.password, user.password):
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail = "Invalid email or password")
    
    access_token = create_access_token({"sub":user.email})

    return ({
        "access token": access_token,
        "type": "bearer"
    })

@router.post('/postjob', response_model=JobResponse)
def post_job(job: JobCreate, r: UsersDB = Depends(recruiter_required), db:Session = Depends(get_db)):
    new_job = JobsDB(title= job.title, company = job.company, created_by = r.id)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    users = db.query(UsersDB).filter(UsersDB.role == "user", UsersDB.is_active == True).all()
    for user in users:
        
        manager.send_to_user(user.id, {"type":"job posted", "job_id":new_job.id, "details":f"{new_job.title} at {new_job.company}"})
    return new_job


@router.get('/search', response_model = List[JobResponse])
def search_job(title:str, p = Depends(pagination), db: Session = Depends(get_db)):
    skip,limit = p

    jobs = db.query(JobsDB).filter(JobsDB.title == title).offset(skip).limit(limit).all()

    return jobs


@router.post('/apply/{job_id}', response_model = ApplicationResponse)
def apply(job_id:int, user: UsersDB = Depends(login_required), db: Session = Depends(get_db)):

    jobs = db.query(JobsDB).filter(JobsDB.id == job_id).first()
    
    if not jobs:
        raise HTTPException(status_code = status.HTTP_204_NO_CONTENT, detail = "Job not found")
    
    existing_application = db.query( ApplicationsDB).filter(ApplicationsDB.user_id == user.id, ApplicationsDB.job_id== job_id).first()
    if existing_application:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = " already applied")
    new_application = ApplicationsDB(user_id = user.id, job_id = job_id, status = "applied")

    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    manager.send_to_user(jobs.created_by, {"type":"applied", "user_id":user.id, "message":f"{user.id} has applied for your job"})
    return new_application


@router.get('/profile/user', response_model = UserResponse)
def user_profile(user: UsersDB = Depends(login_required)):
    return user


@router.get('/profile/user/applications', response_model = List[ApplicationResponse])
def user_applications( user: UsersDB = Depends(login_required),p = Depends(pagination), db: Session = Depends(get_db)):
    skip,limit = p
    applications = db.query(ApplicationsDB).filter(ApplicationsDB.user_id == user.id).offset(skip).limit(limit).all()
    return applications


@router.get('/profile/recruiter', response_model = UserResponse )
def recruiter_profile( recruiter: UsersDB= Depends(recruiter_required)):
    return recruiter


@router.get('/profile/admin', response_model = UserResponse)
def admin_profile(user: UsersDB = Depends(admin_required)):
    return user


@router.get('/profile/recruiter/posts', response_model = List[JobResponse])
def recruiter_posts(recruiter: UsersDB = Depends(recruiter_required), p=Depends(pagination), db: Session = Depends(get_db)):
    skip,limit = p
    posts = db.query(JobsDB).filter(JobsDB.created_by == recruiter.id).offset(skip).limit(limit).all()

    return posts


@router.get('/admin/users', response_model = List[UserResponse])
def get_users(admin: UsersDB = Depends(admin_required), db: Session= Depends(get_db)):
    users = db.query(UsersDB).all()
    return users

@router.patch('/admin/user/deactivate', response_model = UserResponse)
def deactivate_user(user_id:int,admin:UsersDB = Depends(admin_required), db:Session = Depends(get_db)):
    user = db.query(UsersDB).filter(UsersDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = " user not found")
    user.is_active = False
    db.commit()
    manager.send_to_user(user.id, {"message":" your account has been deactivated by the admin"})
    return user
    
@router.get('/admin/user', response_model = UserResponse)
def get_user(user_id:int, admin: UsersDB=Depends(admin_required), db:Session = Depends(get_db) ):
    user = db.query(UsersDB).filter(UsersDB.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = " User not found")
    
    return user


@router.websocket('/ws')
async def websocket_Endpoint(websocket:WebSocket, db: Session = Depends(get_db)):
    
    await websocket.accept()
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code = 1008)
        return 
    
    payload = verify_token(token)
    useremail = payload.get("sub")

    if not useremail:
        await websocket.close(code = 1008 )
        return 
    
    user = db.query(UsersDB).filter(UsersDB.email == useremail).first()
    
    if not user:
        await websocket.close(code = 1008)
        return 
    
    await manager.connect(user.id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user.id)
