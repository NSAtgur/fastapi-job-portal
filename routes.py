from fastapi import Depends, HTTPException, status, APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, BackgroundTasks, Response
from models import UsersDB, ApplicationsDB, JobsDB, NotificationsDB, Experience, Skills, UserSkills, Socials, Projects
from database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from tokens import create_access_token, verify_token
from security import verify_password_hash, generate_password_hash
from schemas import CreateUser, UserResponse, JobCreate, JobResponse, ApplicationResponse, NotificationResponse, UploadResponse, ProfileUpdate, ProjectsCreate, UpdateProjects, ProjectResponse, ExperienceCreate, UpdateExperience, ExperienceResponse, SkillsCreate, UpdateSocials, SkillResponse, SocialsResponse
from sqlalchemy.ext.asyncio import AsyncSession
from auth import login_required, admin_required, recruiter_required, pagination
from typing import List
from ws_manager import manager
from sqlalchemy import or_,select
from sqlalchemy.orm import selectinload
from dotenv import load_dotenv
import os
from worker import process_notification
from PIL import Image
import cloudinary
import cloudinary.uploader
import logging

router = APIRouter()
load_dotenv()

tasks = []

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

logger = logging.getLogger(__name__)



@router.post('/register', response_model=UserResponse)
async def register_user(
            user: CreateUser,
            db: AsyncSession = Depends(get_db
            )):
    
    result = await db.execute( select(UsersDB).where(UsersDB.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered")
    try:
        hashed_password = generate_password_hash(user.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    try:

        new_user = UsersDB(name=user.name, email=user.email, password=hashed_password, role=user.role)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        logger.info("User %s registered", new_user.name)
        return new_user

    except Exception:
        await db.rollback()
        logger.exception("Failed to register %s user", user.name)
        raise

@router.post('/login')
async def login_user(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
        ):
    result = await db.execute(select(UsersDB).where(UsersDB.email == form_data.username))
    user = result.scalar_one_or_none()

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


@router.post('/job', response_model=JobResponse)
async def post_job(
        job: JobCreate,
        background_tasks: BackgroundTasks, 
        r: UsersDB = Depends(recruiter_required), 
        db: AsyncSession = Depends(get_db)
        ):
    try: 
        new_job = JobsDB(title=job.title, company=job.company, salary=job.salary, location=job.location, job_type=job.job_type, created_by=r.id)
        db.add(new_job)
        await db.commit()
        await db.refresh(new_job)
        result = await db.execute(select(UsersDB).where(UsersDB.role == "user", UsersDB.is_active == True))
        users = result.scalars().all()
        user_ids = [user.id for user in users]

        background_tasks.add_task(process_notification, {
            "receiver_id": user_ids,
            "type": "job posted",
            "job_id": new_job.id
        })
        
        logger.info("User %s posted new job", r.name, new_job.title)


        return new_job

    except Exception:
        await db.rollback()
        logger.exception("DB failed to add %s job", job.title)
        raise


    

@router.get('/search', response_model=List[JobResponse])
async def search_job(
    title: str, 
    p=Depends(pagination), 
    db: AsyncSession = Depends(get_db)
    ):
    skip, limit = p
    try:
        results = await db.execute(select(JobsDB).where(or_(JobsDB.title.ilike(f"%{title}%"))).offset(skip).limit(limit))
        jobs = results.scalars().all()
        return jobs

    except Exception:
        logger.exception("Job %s not found", title)
        raise


@router.post('/apply/{job_id}', response_model=ApplicationResponse)
async def apply(job_id: int, background_tasks: BackgroundTasks, user: UsersDB = Depends(login_required), db: AsyncSession = Depends(get_db)):
    job_result = await db.execute(select(JobsDB).where(JobsDB.id == job_id))
    job = job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    application_result = await db.execute(select(ApplicationsDB).where(ApplicationsDB.user_id == user.id, ApplicationsDB.job_id == job_id))
    existing_application = application_result.scalar_one_or_none()
    if existing_application:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already applied")
    try:
        new_application = ApplicationsDB(user_name=user.name,user_id=user.id, job_id=job_id, status="applied")
        db.add(new_application)
        await db.commit()
        await db.refresh(new_application)
        logger.info(f"{user.name} applied for {job.title}")
        background_tasks.add_task(process_notification, {
            "receiver_id": job.created_by,
            "type": "application",
            "user_id": user.id,
            "job_id": job_id
        })
        return new_application

    except Exception:
        await db.rollback()
        logger.exception("DB failed to insert new application")
        raise


    


@router.get('/users/me/profile', response_model=UserResponse)
async def user_profile(user: UsersDB = Depends(login_required)):
    return user

# Routes for user experience(GET,POST,PUT,DELETE)

@router.post('/me/experience', response_model= ExperienceResponse)
async def add_experience(
    experience:ExperienceCreate,
    user: UsersDB = Depends(login_required),
    db: AsyncSession = Depends(get_db)
    ):
    try:
        new_experience = Experience(
                organization_name= experience.organization_name, 
                user_id = user.id,
                role= experience.role, start_date= experience.start_date,
                end_date= experience.end_date, 
                contribution= experience.contribution, 
                currently_working= experience.currently_working, 
                skills_used= experience.skills_used
        )

        db.add(new_experience)
        await db.commit()
        await db.refresh(new_experience)
        logger.info("New experience added")

        return new_experience
    
    except Exception:
        await db.rollback()
        logger.exception("Unable to add experience")
        raise


@router.put('/me/experience/{experience_id}', response_model= ExperienceResponse)
async def update_experience( 
                            experience_id:int, 
                            experience:UpdateExperience, 
                            user: UsersDB = Depends(login_required),
                            db: AsyncSession = Depends(get_db)
                            ):
    
    try:
        existing_experience = await db.execute(select(Experience).where(Experience.id == experience_id, Experience.user_id == user.id ))
        user_exp = existing_experience.scalar_one_or_none()

        if not user_exp:
                raise HTTPException(
                    status_code=404,
                    detail="Experience not found"
                )

        updates = experience.model_dump(exclude_unset=True)

        for field, value in updates.items():
            setattr(user_exp, field, value)
        await db.commit()
        await db.refresh(user_exp)

        logger.info("Updated experience")
        return user_exp
    except Exception:
        await db.rollback()
        logger.exception("DB error")
        raise
        

@router.get('/me/experience', response_model= List[ExperienceResponse])
async def get_experience(
    user:UsersDB = Depends(login_required), 
    db: AsyncSession = Depends(get_db)
    ):
    try:
        existing_user_experience = await db.execute(select(Experience).where(Experience.user_id == user.id))
        user_exp = existing_user_experience.scalars().all()

        if not user_exp:
            return []
        
        return user_exp
    
    except Exception:
        await db.rollback()
        logger.exception("Experience for %s user not found", user.id)
        raise
        
    
@router.delete('/me/experience/{experience_id}')
async def delete_experience(
    experience_id:int,
    user: UsersDB = Depends(login_required),
    db: AsyncSession = Depends(get_db)
):
    try:
        existing_user_exp = await db.execute(select(Experience).where(Experience.id == experience_id, Experience.user_id == user.id))
        user_exp = existing_user_exp.scalar_one_or_none()
        
        if not user_exp:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = "user experience not found")
        
        db.delete(user_exp)
        await db.commit()

        return Response(status_code= status.HTTP_204_NO_CONTENT)
    
    except Exception:
        await db.rollback()
        logger.exception("Unable to delete experience")
        raise


#Routes for projects of users(GET,POST,PUT,DELETE)
@router.get('/me/projects', response_model = List[ ProjectResponse])
async def get_projects(user:UsersDB = Depends(login_required),p = Depends(pagination), db:AsyncSession = Depends(get_db)):
    skip,limit = p
    try:
        existing_project= await db.execute(select(Projects).where(Projects.user_id == user.id).offset(skip).limit(limit))
        projects = existing_project.scalars().all()

        if not projects:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = "Projects not found")
        
        logger.info("Fetched the projects for %s user", user.id)
        return projects
    except Exception:
        logger.exception("DB error")
        raise


@router.post('/me/projects', response_model=ProjectResponse)
async def add_project(
    project: ProjectsCreate, 
    user:UsersDB = Depends(login_required), 
    db:AsyncSession = Depends(get_db)
    ):
    try:
        new_project = Projects(
            title = project.title,
            user_id = user.id,
            description = project.description,
            github_link = project.github_link,
            live_url = project.live_url
        )

        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)
        logger.info("Added new project for %s user", user.id)

        return new_project
    except Exception:
        await db.rollback()
        logger.exception("DB error")
        raise


@router.put('/me/projects/{project_id}', response_model=ProjectResponse)
async def update_project(
    project_id:int, 
    project:UpdateProjects, 
    user:UsersDB = Depends(login_required), 
    db:AsyncSession = Depends(get_db)
    ):
    try:
        existing_project = await db.execute(select(Projects).where(Projects.id == project_id,Projects.user_id == user.id))
        user_project = existing_project.scalar_one_or_none()

        if not user_project:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = "Project not found")
        
        updates = project.model_dump(exclude_unset=True)

        for field, value in updates.items():
            setattr(user_project, field, value)

        await db.commit()
        await db.refresh(user_project)

        logger.info("Updated % user project %s", user.id, project_id)
        return user_project
    
    except Exception:
        await db.rollback()
        logger.exception("DB error")
        raise


@router.delete('/me/projects/{project_id}')
async def delete_project(
    project_id:int,
    user:UsersDB = Depends(login_required),
    db:AsyncSession = Depends(get_db)
):
    try:
        existing_project = await db.execute(select(Projects).where(Projects.id == project_id, Projects.user_id == user.id))
        user_project = existing_project.scalar_one_or_none()

        if not user_project:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = "Project not found")
        
        db.delete(user_project)
        await db.commit()

        logger.info("Deleted %s user %s project", user.id, project_id)

        return Response(status_code= status.HTTP_204_NO_CONTENT)
    
    except Exception:
        await db.rollback()
        logger.exception("DB error")
        raise


#Routes for skills GET, POST
@router.get('/me/skills', response_model= List[SkillResponse])
async def get_skills(
    user:UsersDB = Depends(login_required), 
    db:AsyncSession = Depends(get_db)
    ):

    try:
        existing_skills = await db.execute(select(UserSkills).options(selectinload(UserSkills.skills)).where(UserSkills.user_id == user.id))
        user_skills = existing_skills.scalars().all()

        if not user_skills:
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail = "Skills not added"
            )
        return [mapping.skills for mapping in user_skills]
    
    except Exception:
        logger.exception("DB error")
        raise


@router.post('/me/skills', response_model= SkillResponse)
async def add_skills(
    skills: SkillsCreate, 
    user:UsersDB = Depends(login_required),
    db:AsyncSession = Depends(get_db)
    ):
    
    try:
        #Check if the skill is already in the Skills table
        new_skill = await db.execute(select(Skills).where(Skills.skill_name == skills.skill_name))
        user_skill = new_skill.scalar_one_or_none()
        
        #If the skill is not added in the table store it 
        if user_skill is None:
            user_skill = Skills(skill_name = skills.skill_name)
            db.add(user_skill)
            await db.flush()
            
        existing_user_skill = await db.execute(select(UserSkills).where(UserSkills.skill_id == user_skill.id, UserSkills.user_id == user.id))
        existing_skill = existing_user_skill.scalar_one_or_none()

        if existing_skill:
            raise HTTPException(
                status_code= status.HTTP_409_CONFLICT,
                detail="Skill already added"
            )
        
        skill = UserSkills(skill_id = user_skill.id, user_id = user.id)
        db.add(skill)        

        await db.commit()

        logger.info("Added skill for %s user", user.id)
        
        return {
            "id":skill.skill_id,
            "user_id":skill.user_id,
            "skill_name":skill.skills.skill_name
        }
    
    except Exception:
        await db.rollback()
        logger.exception("DB error")
        raise


# Routes for adding social platform profile links (GET, POST, DELETE)
@router.get('/me/socials', response_model=List[SocialsResponse])
async def get_socials(
    user:UsersDB = Depends(login_required),
    db:AsyncSession = Depends(get_db)
):
    try:
        existing_socials = await db.execute(select(Socials).where(Socials.user_id == user.id))
        socials = existing_socials.scalars().all()

        if not socials:
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail = "Socials not found"
            )
        
        return socials
    
    except Exception:
        await db.rollback()
        logger.exception("DB error")
        raise


@router.put('/me/socials/{social_id}', response_model= SocialsResponse)
async def add_socials(
    socials:UpdateSocials,
    social_id:int,
    user:UsersDB = Depends(login_required),
    db:AsyncSession = Depends(get_db)
):
    try:
        existing_socials = await db.execute(select(Socials).where(Socials.user_id == user.id, Socials.id == social_id))
        user_socials = existing_socials.scalar_one_or_none()

        if not user_socials:
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail= "Social links not found for the user"
            )
        
        updates = socials.model_dump(exclude_unset=True)

        for field, value in updates.items():
            setattr(user_socials, field, value)
        await db.commit()
        await db.refresh(user_socials)
        logger.info("Added socials for % user", user.id )

        return user_socials
    
    except Exception:
        await db.rollback()
        logger.exception("DB error")
        raise


@router.delete('/me/socials/{social_id}')
async def delete_socials(
    social_id:int,
    user:UsersDB = Depends(login_required),
    db:AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Socials).where(Socials.user_id == user.id, Socials.id ==social_id))
        user_social = result.scalar_one_or_none()

        if not user_social:
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail="Socials link not found"
            )
        db.delete(user_social)
        await db.commit()

        logger.info("Deleted %s social for %s user", social_id, user.id)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception:
        await db.rollback()
        logger.exception("DB error")        
        raise


@router.get('/users/{user_id}', response_model= UserResponse )
async def get_user_profile(
    user_id:int,
    db:AsyncSession = Depends(get_db)
):
    try:
        existing_user = await db.execute(select(UsersDB).where(UsersDB.id == user_id))
        user = existing_user.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
        return user
    
    except Exception:

        logger.exception("DB error")
        raise


@router.get('/user/{user_id}/experience', response_model = List[ExperienceResponse])
async def get_user_experience(
    user_id:int,
    db:AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Experience).where(Experience.user_id== user_id))
        user_experience = result.scalars().all()

        if not user_experience:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail= "Experience not found"
            )
        
        return user_experience
    
    except Exception:
        logger.exception("DB error")
        raise


@router.get('/user/{user_id}/skills', response_model= List[SkillResponse])
async def get_user_skills(
    user_id:int,
    db:AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(UserSkills).options(selectinload(UserSkills.skills)).where(UserSkills.user_id == user_id))
        user_skills = result.scalars().all()

        if not user_skills:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail= "Skills not found"
            )
        return [mapping.skills for mapping in user_skills]
    
    except Exception:
        logger.exception("DB error")
        raise


@router.get('/user/{user_id}/projects', response_model = List[ProjectResponse])
async def get_user_projects(
    user_id:int,
    db:AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Projects).where(Projects.user_id== user_id))
        user_projects = result.scalars().all()

        if not user_projects:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail= "Projects not found"
            )
        
        return user_projects
    
    except Exception:
        logger.exception("DB error")
        raise    


@router.get('/user/{user_id}/socials', response_model = List[SocialsResponse])
async def get_user_socials(
    user_id:int,
    db:AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Socials).where(Socials.user_id== user_id))
        user_socials = result.scalars().all()

        if not user_socials:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail= "Socials not found"
            )
        
        return user_socials
    
    except Exception:
        logger.exception("DB error")
        raise


@router.get('/users/me/applications', response_model=List[ApplicationResponse])
async def user_applications(
    user: UsersDB = Depends(login_required), 
    p=Depends(pagination), 
    db: AsyncSession = Depends(get_db)
    ):
    skip, limit = p

    try:
        result = await db.execute(select(ApplicationsDB).where(ApplicationsDB.user_id == user.id).offset(skip).limit(limit))
        applications = result.scalars().all()

        if not applications:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND)
        
        return applications

    except Exception:
        await db.rollback()
        logger.exception("Failed to fetch the application")
        raise 


@router.get('/users/recruiter/profile', response_model=UserResponse)
async def recruiter_profile(recruiter: UsersDB = Depends(recruiter_required)):
    return recruiter


@router.get('/users/admin/profile', response_model=UserResponse)
async def admin_profile(user: UsersDB = Depends(admin_required)):
    return user


@router.get('/users/recruiter/posts', response_model=List[JobResponse])
async def recruiter_posts(recruiter: UsersDB = Depends(recruiter_required), p=Depends(pagination), db: AsyncSession = Depends(get_db)):
    skip, limit = p
    try:
        existing_posts = await db.execute(select(JobsDB).where(JobsDB.created_by == recruiter.id).offset(skip).limit(limit))
        posts = existing_posts.scalars().all()
        return posts

    except Exception:
        logger.exception()
        raise


@router.delete('/users/recruiter/posts/delete/{job_id}', response_model=JobResponse)
async def delete_jobposts(job_id: int, background_tasks: BackgroundTasks, recruiter: UsersDB = Depends(recruiter_required), db: AsyncSession = Depends(get_db)):
    existing_job =await db.execute(select (JobsDB).where(JobsDB.id == job_id, JobsDB.created_by == recruiter.id))
    job = existing_job.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    # save details before deleting
    job_title = job.title
    job_company = job.company
    try: 
        db.delete(job)
        await db.commit()
        logger.info("User %s deleted the job posting", recruiter.name, job.title)

        background_tasks.add_task(process_notification, {
            "receiver_id": recruiter.id,
            "type": "job deleted",
            "job_title": job_title,
            "job_company": job_company
        })
 
        return job

    except Exception:
        await db.rollback()
        logger.exception("Failed to delete %s job", job_id)




@router.get('/admin/users', response_model=List[UserResponse])
async def get_users(admin: UsersDB = Depends(admin_required), p=Depends(pagination), db: AsyncSession = Depends(get_db)):
    skip, limit = p
    result = await db.execute(select(UsersDB).offset(skip).limit(limit))
    users = result.scalars().all()
    return users


@router.patch('/admin/user/deactivate', response_model=UserResponse)
async def deactivate_user(user_id: int, background_tasks: BackgroundTasks, admin: UsersDB = Depends(admin_required), db: AsyncSession = Depends(get_db)):
    existing_user = await db.execute(select(UsersDB).where(UsersDB.id == user_id))
    user = existing_user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    try:
        user.is_active = False
        await db.commit()
        logger.info("Admin deactivated user %s", user.name)
        background_tasks.add_task(process_notification, {
        "receiver_id": user_id,
        "type": "deactivated"
        })

        return user

    
    except Exception:
        logger.exception("Failed to deactivate %s user", user.name)
        raise


    


@router.patch('/admin/user/activate', response_model=UserResponse)
async def activate_user(user_id: int, background_tasks: BackgroundTasks, admin: UsersDB = Depends(admin_required), db: AsyncSession = Depends(get_db)):
    existing_user = await db.execute(select(UsersDB).where(UsersDB.id == user_id))
    user = existing_user.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already active")
    try:
        user.is_active = True
        await db.commit()
        await db.refresh(user)
        logger.info("User %s activated successful", user.name)
        background_tasks.add_task(process_notification, {
        "receiver_id": user_id,
        "type": "activated"
        })

        return user
    
    except Exception:
        await db.rollback()
        logger.exception("Failed to activate %s user", user.name)
        raise
    




@router.get('/admin/user', response_model=UserResponse)
async def get_user(user_id: int, admin: UsersDB = Depends(admin_required), db: AsyncSession = Depends(get_db)):
    existing_user = await db.execute(select(UsersDB).where(UsersDB.id == user_id))
    user= existing_user.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    return user


@router.get('/admin/promote-admin', response_model=UserResponse)
async def promote_user(user_id: int, admin: UsersDB = Depends(admin_required), db: AsyncSession = Depends(get_db)):
    existing_user =await db.execute(select(UsersDB).where(UsersDB.id == user_id))
    user = existing_user.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.get('/profile/notifications', response_model=List[NotificationResponse])
async def notifications(user=Depends(login_required), p=Depends(pagination), db: AsyncSession = Depends(get_db)):
    skip, limit = p
    results = await db.execute(select(NotificationsDB).where(NotificationsDB.user_id == user.id).order_by(NotificationsDB.id.desc()).offset(skip).limit(limit))
    notifications = results.scalars().all()
    logger.info("Notifications found")
    return notifications


@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
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

    result = await db.execute(select(UsersDB).where(UsersDB.email == useremail))
    user = result.scalar_one_or_none()

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
        raise


@router.post('/profile/upload', response_model=UploadResponse)
async def upload_pic(file: UploadFile = File(...), user=Depends(login_required), db: AsyncSession = Depends(get_db)):
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
    
    try:
        user.profile_pic = image_url
        user.profile_pic_public_id = public_id
        await db.commit()
        await db.refresh(user)
        logger.info("Profile pic uploaded")
        return {"image_url": image_url}

    except Exception:
        await db.rollback()
        logger.exception("DB failed")
        raise



    
    