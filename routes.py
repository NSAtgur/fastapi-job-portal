from fastapi import Depends, HTTPException, status, APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, BackgroundTasks, Response
from models import UsersDB, ApplicationsDB, JobsDB, NotificationsDB, Experience, Skills, UserSkills, Socials, Projects
from database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from tokens import create_access_token, verify_token
from security import verify_password_hash, generate_password_hash
from schemas import CreateUser, UserResponse, JobCreate, JobResponse, ApplicationResponse, NotificationResponse, UploadResponse, ProfileUpdate, ProjectsCreate, UpdateProjects, ProjectResponse, ExperienceCreate, UpdateExperience, ExperienceResponse, SkillsCreate, UpdateSocials, SkillResponse, SocialsResponse,ApplicationStatusUpdate,JobsStatusUpdate, JobStatus,JobSearchResponse
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
from datetime import datetime

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


@router.post('/jobs', response_model=JobResponse)
async def post_job(
        job: JobCreate,
        background_tasks: BackgroundTasks, 
        r: UsersDB = Depends(recruiter_required), 
        db: AsyncSession = Depends(get_db)
        ):
    try: 
        new_job = JobsDB(title=job.title, company=job.company, salary=job.salary, location=job.location, job_type=job.job_type, created_by=r.id, requirements = job.requirements)
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
        
        logger.info("User user_id=%s posted new job", r.name, new_job.title)


        return new_job

    except Exception:
        await db.rollback()
        logger.exception("DB failed to add job_title=%s job posted by recruiter_id=%s recruiter", job.title, r.id)
        raise


    

@router.get('/jobs', response_model=List[JobSearchResponse])
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
        logger.exception("Failed to fetch - jobs job_title=%s", title)
        raise

@router.get('/jobs/{job_id}', response_model= JobResponse)
async def get_job_details(
    job_id:int,
    db:AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(JobsDB).where(JobsDB.id == job_id))
        job = result.scalar_one_or_none()

        if not job:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Job not found")

        return job

    except Exception:
        logger.exception("Failed to fetch job job_id=%s ", job_id)
        raise

@router.post('/jobs/{job_id}/apply', response_model=ApplicationResponse)
async def apply(job_id: int, background_tasks: BackgroundTasks, user: UsersDB = Depends(login_required), db: AsyncSession = Depends(get_db)):
    job_result = await db.execute(select(JobsDB).where(JobsDB.id == job_id))
    job = job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if job.status == JobStatus.closed.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job is not accepting applications")

    application_result = await db.execute(select(ApplicationsDB).where(ApplicationsDB.user_id == user.id, ApplicationsDB.job_id == job_id))
    existing_application = application_result.scalar_one_or_none()
    if existing_application:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already applied")
    try:
        new_application = ApplicationsDB(user_name=user.name,user_id=user.id, job_id=job_id)

        logger.info("User %s is applying for %s job ", user.id, job_id)

        db.add(new_application)

        logger.info("Commiting the application")
        await db.commit()
        logger.info("Successfully commited the new application")
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
        logger.exception("DB failed to insert new application for job_id=%s job by user_id=%s user", job_id, user.id )
        raise


@router.patch('/users/me', response_model = UserResponse)
async def update_profile(
    profile:ProfileUpdate,
    user:UsersDB = Depends(login_required),
    db:AsyncSession = Depends(get_db)
):
    
    try:
        result = await db.execute(select(UsersDB).where(UsersDB.id == user.id))
        existing_user = result.scalar_one_or_none()

        updates = profile.model_dump(exclude_unset=True)

        for field,value in updates.items():
            setattr(existing_user, field, value)

        await db.commit()
        await db.refresh(existing_user)

        return existing_user
    
    except Exception:
        await db.rollback()
        logger.exception("DB failed to fetch the profile of user_id=%s user", user.id)
        raise

@router.get('/users/me', response_model=UserResponse)
async def user_profile(user: UsersDB = Depends(login_required)):
    return user

# Routes for user experience(GET,POST,PUT,DELETE)

@router.post('/users/me/experience', response_model= ExperienceResponse)
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
        
        logger.info("Adding experience for %s user", user.id)

        db.add(new_experience)

        logger.info("Commiting new experience")

        await db.commit()

        logger.info("Commited experience details for %s user", user.id)
        
        await db.refresh(new_experience)
        logger.info("New experience added by user user_id=%s ", user.id)

        return ExperienceResponse(
            id=new_experience.id,
            organization_name=new_experience.organization_name,
            role=new_experience.role,
            start_date=new_experience.start_date,
            end_date=new_experience.end_date,
            contribution=new_experience.contribution,
            currently_working=new_experience.currently_working,
            skills_used=new_experience.skills_used,
            created_at=new_experience.created_at or datetime.utcnow(),
        )
    
    except Exception:
        await db.rollback()
        logger.exception("Unable to add experience for user_id=%s user", user.id)
        raise


@router.put('/users/me/experience/{experience_id}', response_model= ExperienceResponse)
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
        
        logger.info("Updating %s experience of user user_id=%s", experience_id, user.id)

        updates = experience.model_dump(exclude_unset=True)

        for field, value in updates.items():
            setattr(user_exp, field, value)

        
        await db.commit()
        
        logger.info("Successfully commited changes for user_id=%s user ", user.id)

        await db.refresh(user_exp)

        logger.info("Updated experience for %s user", user.id)

        return ExperienceResponse(
            id=user_exp.id,
            organization_name=user_exp.organization_name,
            role=user_exp.role,
            start_date=user_exp.start_date,
            end_date=user_exp.end_date,
            contribution=user_exp.contribution,
            currently_working=user_exp.currently_working,
            skills_used=user_exp.skills_used,
            created_at=user_exp.created_at or datetime.utcnow(),
        )
    except Exception:
        await db.rollback()
        logger.exception("DB failed to update the experience for user_id%s user", user.id)
        raise
        

@router.get('/users/me/experience', response_model= List[ExperienceResponse])
async def get_experience(
    user:UsersDB = Depends(login_required), 
    db: AsyncSession = Depends(get_db)
    ):
    try:
        existing_user_experience = await db.execute(select(Experience).where(Experience.user_id == user.id))
        user_exp = existing_user_experience.scalars().all()

        if not user_exp:
            return []
        

        return [
            ExperienceResponse(
                id=exp.id,
                organization_name=exp.organization_name,
                role=exp.role,
                start_date=exp.start_date,
                end_date=exp.end_date,
                contribution=exp.contribution,
                currently_working=exp.currently_working,
                skills_used=exp.skills_used,
                created_at=exp.created_at or datetime.utcnow(),
            )
            for exp in user_exp
        ]
    
    except Exception:
        await db.rollback()
        logger.exception("Experience for user_id=%s user not found", user.id)
        raise
        
    
@router.delete('/users/me/experience/{experience_id}')
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
        
        logger.info("Deleting experience_id=%s experience of user_id%s user ", experience_id, user.id)

        await db.delete(user_exp)

        logger.info("Commiting the changes after deleting experience_id=%s experience", experience_id)

        await db.commit()
        logger.info("successfully commited the changees and deleted the experience_id=%s experience", experience_id)

        return Response(status_code= status.HTTP_204_NO_CONTENT)
    
    except Exception:
        await db.rollback()
        logger.exception("Unable to delete experience experience_id=%s for user_id=%s user", experience_id, user.id)
        raise


#Routes for projects of users(GET,POST,PUT,DELETE)
@router.get('/users/me/projects', response_model = List[ ProjectResponse])
async def get_projects(user:UsersDB = Depends(login_required),p = Depends(pagination), db:AsyncSession = Depends(get_db)):
    skip,limit = p
    try:
        existing_project= await db.execute(select(Projects).where(Projects.user_id == user.id).offset(skip).limit(limit))
        projects = existing_project.scalars().all()
        
        if not projects:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = "Projects not found")
        
        logger.info("Fetched the projects for %s user", user.id)
        return [
            ProjectResponse(
                id=project.id,
                title=project.title,
                description=project.description,
                github_link=project.github_link,
                live_url=project.live_url,
                created_at=project.created_at or datetime.utcnow(),
            )
            for project in projects
        ]
    except Exception:
        logger.exception("DB failed to load the projects of user_id=%s user", user.id)
        raise


@router.post('/users/me/projects', response_model=ProjectResponse)
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
            github_link = str(project.github_link),
            live_url = str(project.live_url)
        )
        
        logger.info("Adding a new project for user_id=%s user", user.id)
        db.add(new_project)

        logger.info("Commiting the changes")

        await db.commit()

        logger.info("Successfully commited the changes")
        await db.refresh(new_project)
        logger.info("Added new project for %s user", user.id)

        return ProjectResponse(
            id=new_project.id,
            title=new_project.title,
            description=new_project.description,
            github_link=new_project.github_link,
            live_url=new_project.live_url,
            created_at=new_project.created_at or datetime.utcnow(),
        )
    except Exception:
        await db.rollback()
        logger.exception("DB failed to add new project of user_id=%s user", user.id)
        raise


@router.put('/users/me/projects/{project_id}', response_model=ProjectResponse)
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

        logger.info("Updated %s user project %s", user.id, project_id)
        return ProjectResponse(
            id=user_project.id,
            title=user_project.title,
            description=user_project.description,
            github_link=user_project.github_link,
            live_url=user_project.live_url,
            created_at=user_project.created_at or datetime.utcnow(),
        )
    
    except Exception:
        await db.rollback()
        logger.exception("DB failed to update project_id=%s of user_id=%s", project_id, user.id)
        raise


@router.delete('/users/me/projects/{project_id}')
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
        
        await db.delete(user_project)
        await db.commit()

        logger.info("Deleted %s user %s project", user.id, project_id)

        return Response(status_code= status.HTTP_204_NO_CONTENT)
    
    except Exception:
        await db.rollback()
        logger.exception("DB failed to add new project for user_id=%s user", user.id)
        raise



#Routes for skills GET, POST
@router.get('/users/me/skills', response_model= List[SkillResponse])
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
        return [
            SkillResponse(
                id=mapping.skill_id,
                skill_name=mapping.skills.skill_name,
                created_at=mapping.created_at or datetime.utcnow(),
            )
            for mapping in user_skills
        ]
    
    except Exception:
        logger.exception("DB failed to load skills for user_id=%s user",user.id)
        raise


@router.post('/users/me/skills', response_model= SkillResponse)
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
        
        logger.info("Adding the skills for user_id=%s user", user.id)
        
        skill = UserSkills(skill_id = user_skill.id, user_id = user.id)
        db.add(skill)        
        
        logger.info("Commiting the insert")
        await db.commit()

        logger.info("Added skill_id=%s skill for %s user", user.id,skill.skill_id)
        
        return SkillResponse(
            id=skill.skill_id,
            skill_name=user_skill.skill_name,
            created_at=skill.created_at or datetime.utcnow(),
        )
    
    except Exception:
        await db.rollback()
        logger.exception("DB failed to add new skills for user_id=%s user", user.id)
        raise


# Routes for adding social platform profile links (GET, POST, DELETE)
@router.get('/users/me/socials', response_model=List[SocialsResponse])
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
        logger.exception("DB failed to load socials for user_id=%s user", user.id)
        raise


@router.patch("/users/me/socials", response_model=SocialsResponse)
async def update_socials(
    socials: UpdateSocials,
    user: UsersDB = Depends(login_required),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(Socials).where(Socials.user_id == user.id)
        )
        existing_socials = result.scalar_one_or_none()

        if existing_socials is None:
            existing_socials = Socials(user_id=user.id)
            db.add(existing_socials)

        updates = socials.model_dump(exclude_unset=True)

        for field, value in updates.items():
            if value is not None:
                setattr(existing_socials, field, str(value))

        logger.info("Commiting the update")

        await db.commit()
        await db.refresh(existing_socials)

        logger.info("Updated socials for user %s", user.id)

        return SocialsResponse(
            id=existing_socials.id,
            github_profile_url=existing_socials.github_profile_url,
            linkedin_profile_url=existing_socials.linkedin_profile_url,
            leetcode_profile_url=existing_socials.leetcode_profile_url,
            codeforces_profile_url=existing_socials.codeforces_profile_url,
            portfolio_profile_url=existing_socials.portfolio_profile_url,
            created_at=existing_socials.created_at,
        )

    except Exception:
        await db.rollback()
        logger.exception("Unable to update socials for user user_id=%s", user.id)
        raise


@router.delete('/users/me/socials/{social_id}')
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
        await db.delete(user_social)
        await db.commit()

        logger.info("Deleted %s social for %s user", social_id, user.id)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception:
        await db.rollback()
        logger.exception("DB failed to delete the social link of the user user_id=%s", user.id)        
        raise


# Routes for recruiter to view applicant profile

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
        
        logger.info("got user profile")
        return user
    
    except Exception:

        logger.exception("DB failed to fetch the profile of user_id=%s user", user_id)
        raise 


@router.get('/users/{user_id}/experience', response_model = List[ExperienceResponse])
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
        logger.exception("DB failed to get the experience of user_id=%s user", user_id)
        raise


@router.get('/users/{user_id}/skills', response_model= List[SkillResponse])
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
        return [SkillResponse(
            id = mapping.id,
            skill_name= mapping.skills.skill_name,
            created_at= mapping.created_at
            )
            for mapping in user_skills
        ]
    
    except Exception:
        logger.exception("DB failed to fetch the skills of user_id=%s user", user_id)
        raise


@router.get('/users/{user_id}/projects', response_model = List[ProjectResponse])
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
        logger.exception("DB failed to fetch the projects of user_id=%s user", user_id)
        raise    


@router.get('/users/{user_id}/socials', response_model = List[SocialsResponse])
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
        logger.exception("DB failed to fetch user socials of user_id=%s user", user_id)
        raise


@router.get('/users/me/applications', response_model=List[ApplicationResponse])
async def user_applications(
    user: UsersDB = Depends(login_required), 
    p=Depends(pagination), 
    db: AsyncSession = Depends(get_db)
    ):
    skip, limit = p

    try:
        result = await db.execute(
                    select(ApplicationsDB)
                    .options(selectinload(ApplicationsDB.job))
                    .where(ApplicationsDB.user_id == user.id)
                )

        applications = result.scalars().all()
        user_id = user.id

        if not applications:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND)
        
        return  [
                    ApplicationResponse
                    (
                        id=application.id,
                        user_name = user.name,
                        user_id = user.id,
                        job_id = application.job_id,
                        job_title=application.job.title,
                        status = application.status,
                        applied_at = application.applied_at
                    )
                    for application in applications
                ]

    except Exception:
        await db.rollback()
        logger.exception("Failed to fetch the applications of user_id=%s user", user_id)
        raise 

#Route for recruiter to view applications 

@router.get('/users/recruiter/posts/{job_id}/applications', response_model=List[ApplicationResponse])
async def recruiter_applications(
    job_id: int,
    recruiter: UsersDB = Depends(recruiter_required),
    p=Depends(pagination),
    db: AsyncSession = Depends(get_db)
):
    skip, limit = p

    try:
        job_result = await db.execute(
            select(JobsDB).where(JobsDB.id == job_id, JobsDB.created_by == recruiter.id)
        )
        job = job_result.scalar_one_or_none()

        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        result = await db.execute(
            select(ApplicationsDB)
            .where(ApplicationsDB.job_id == job_id)
            .order_by(ApplicationsDB.applied_at.desc())
            .offset(skip)
            .limit(limit)
        )
        applications = result.scalars().all()

        if not applications:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return applications

    except Exception:
        await db.rollback()
        logger.exception("Failed to fetch recruiter applications for job_id=%s job", job_id)
        raise

@router.patch('/users/recruiter/posts/{job_id}', response_model= JobResponse)
async def update_job_status( 
    data:JobsStatusUpdate,
    job_id:int,
    background_tasks:BackgroundTasks,
    recruiter:UsersDB = Depends(recruiter_required),
    db:AsyncSession = Depends(get_db)
):

    try:
        result = await db.execute(select(JobsDB).where(JobsDB.id == job_id, JobsDB.created_by == recruiter.id))
        job = result.scalar_one_or_none()

        if not job:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                                detail=" job not found")

        job.status = data.status

        logger.info("Recruiter user_id=%s updated the status of job_id=%s job", recruiter.id, job_id)

        await db.commit()
        await db.refresh(job)

        logger.info("Successfully commited and updated job_id=%s job status by recruiter_id=%s recruiter", job_id, recruiter.id)
        background_tasks.add_task(process_notification, {
            "type": "job status updated",
            "receiver_id": recruiter.id,
            "job_title": job.title,
            "company": job.company,
            "status": job.status,
        }
        )

        return job
    except Exception:
        await db.rollback()
        logger.exception("Failed to update status of job job_id=%s", job_id)
        raise


@router.get('/users/recruiter/posts', response_model=List[JobResponse])
async def recruiter_posts(recruiter: UsersDB = Depends(recruiter_required), p=Depends(pagination), db: AsyncSession = Depends(get_db)):
    skip, limit = p
    try:
        existing_posts = await db.execute(select(JobsDB).where(JobsDB.created_by == recruiter.id).offset(skip).limit(limit))
        posts = existing_posts.scalars().all()
        return posts

    except Exception:
        logger.exception("DB failed to fetch the posts of recruiter recruiter_id=%s", recruiter.id)
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
        await db.delete(job)
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
        logger.exception("Failed to delete job_id=%s job", job_id)




@router.get('/admin/users', response_model=List[UserResponse])
async def get_users(admin: UsersDB = Depends(admin_required), p=Depends(pagination), db: AsyncSession = Depends(get_db)):
    skip, limit = p
    result = await db.execute(select(UsersDB).offset(skip).limit(limit))
    users = result.scalars().all()
    return users


@router.patch('/admin/users/{user_id}/deactivate', response_model=UserResponse)
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
        logger.exception("Failed to deactivate user_id=%s user", user.name)
        raise


    


@router.patch('/admin/users/{user_id}/activate', response_model=UserResponse)
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
        logger.exception("Failed to activate user_id=%s user", user.name)
        raise
    




@router.get('/users/me/notifications', response_model=List[NotificationResponse])
async def notifications(user=Depends(login_required), p=Depends(pagination), db: AsyncSession = Depends(get_db)):
    skip, limit = p
    results = await db.execute(select(NotificationsDB).where(NotificationsDB.user_id == user.id).order_by(NotificationsDB.id.desc()).offset(skip).limit(limit))
    notifications = results.scalars().all()
    logger.info("Notifications found for user_id=%s user", user.id)
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


@router.patch('/recruiter/posts/{job_id}/applications/{application_id}', response_model=ApplicationResponse)
async def update_application_status(
    application_id:int,
    data:ApplicationStatusUpdate,
    background_tasks:BackgroundTasks,
    user:UsersDB = Depends(recruiter_required),
    db: AsyncSession = Depends(get_db)
):
    
    try:

        result = await db.execute(select(ApplicationsDB).options(selectinload(ApplicationsDB.job)).where(ApplicationsDB.id == application_id))
        existing_application = result.scalar_one_or_none()

        if not existing_application:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                                detail="Application not found")
        
        existing_application.status = data.status

        logger.info("Entered status for %s application", application_id)
        await db.commit()
        await db.refresh(existing_application)
        logger.info("Updated status for application application_id=%s", application_id)

        background_tasks.add_task(process_notification, {
            "type": "application status updated",
            "receiver_id": existing_application.user_id,
            "job_title": existing_application.job.title,
            "company": existing_application.job.company,
            "status": existing_application.status
        }
        )
        return existing_application
    
    except Exception:
        await db.rollback()
        logger.exception("DB failed to update status of application_id=%s application", application_id)
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
        logger.exception("DB failed to upload the profile pic of user_id=%s user", user.id)
        raise



    
    