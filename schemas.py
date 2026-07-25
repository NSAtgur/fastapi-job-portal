from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl
from datetime import datetime
from typing import Dict, Any
from enum import Enum
from sqlalchemy import Enum as SQLEnum

class ApplicationStatus(str, Enum):
    pending = "Pending"
    review = "In Review"
    interview = "Interview Scheduled"
    accepted = "Accepted"
    rejected = "Rejected"

class JobStatus(str, Enum):
    open = "Open"
    closed = "Closed"
    
class ApplicationStatusUpdate(BaseModel):
    status:ApplicationStatus

class JobsStatusUpdate(BaseModel):
    status: JobStatus
class CreateUser(BaseModel):
    name:str = Field(min_length=8, max_length=15)
    email:EmailStr
    password:str = Field(min_length=8)
    role:str
    profile_pic:str| None = None
    
    model_config = ConfigDict(from_attributes=True)
    
class UserResponse(BaseModel):
    id:int
    name:str
    email:EmailStr
    role:str
    profile_pic:HttpUrl| None = None
    is_active:bool
    is_verified:bool
    experience_years:int | None = None
    bio:str| None = None
    headline:str| None = None
    education:str| None = None
    created_at: datetime


    model_config = ConfigDict(from_attributes=True)

class JobCreate(BaseModel):
    title:str = Field(min_length=8, max_length=20)
    company:str = Field(min_length=8, max_length=30)
    salary:int
    requirements:str
    location:str = Field(min_length= 8, max_length=100)
    job_type:str

    model_config = ConfigDict(from_attributes=True)

class JobResponse(BaseModel):
    id:int
    title:str
    company:str
    salary:int
    status:JobStatus
    requirements:str| None = None
    location:str
    job_type:str
    created_at:datetime

    model_config = ConfigDict(from_attributes=True)

class JobSearchResponse(BaseModel):
    id:int
    title:str
    company:str
    created_at:datetime

    model_config = ConfigDict(from_attributes=True)


class JobApply(BaseModel):
    pass

    model_config = ConfigDict(from_attributes=True)


class ApplicationResponse(BaseModel):
    id:int
    user_name:str | None = None
    user_id:int
    job_id:int
    status:ApplicationStatus
    applied_at:datetime
    
    model_config = ConfigDict(from_attributes=True)

class NotificationResponse(BaseModel):
    id:int
    message:str
    created_at:datetime

    model_config = ConfigDict(from_attributes=True)

class UploadResponse(BaseModel):
    image_url:str| None = None
    model_config = ConfigDict(from_attributes = True)

class ProfileUpdate(BaseModel):
    name:str| None = None
    bio:str| None = None
    headline:str| None = None
    education:str| None = None
    experience_years:int | None = None
    
    model_config = ConfigDict(from_attributes = True)

class ExperienceCreate(BaseModel):
    organization_name:str
    role:str
    start_date:datetime
    end_date:datetime
    contribution:str
    currently_working:bool 
    skills_used:str| None = None

    model_config = ConfigDict(from_attributes = True)

class UpdateExperience(BaseModel):
    organization_name:str| None = None
    role:str| None = None
    start_date:datetime| None = None
    end_date:datetime| None = None
    contribution:str| None = None
    currently_working:bool | None = None
    skills_used:str| None = None

    model_config = ConfigDict(from_attributes = True)


class ExperienceResponse(BaseModel):
    id:int
    organization_name:str
    role:str
    start_date:datetime
    end_date:datetime
    contribution:str
    currently_working:bool 
    skills_used:str| None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)


class ProjectsCreate(BaseModel):
    title:str
    description:str
    github_link:HttpUrl
    live_url:HttpUrl| None = None

    model_config = ConfigDict(from_attributes = True)


class UpdateProjects(BaseModel):
    title:str| None = None
    description:str| None = None
    github_link:HttpUrl| None = None
    live_url:HttpUrl|None = None

    model_config = ConfigDict(from_attributes = True)


class ProjectResponse(BaseModel):
    id:int
    title:str
    description:str
    github_link:HttpUrl
    live_url:HttpUrl| None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)
        

class SkillsCreate(BaseModel):
    skill_name:str

    
    model_config = ConfigDict(from_attributes = True)

class SkillResponse(BaseModel):
    id:int
    skill_name:str| None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)


class UpdateSocials(BaseModel):
    github_profile_url:HttpUrl| None = None
    linkedin_profile_url:HttpUrl| None = None
    leetcode_profile_url:HttpUrl| None = None
    codeforces_profile_url:HttpUrl| None = None
    portfolio_profile_url:HttpUrl| None = None

    model_config = ConfigDict(from_attributes = True)

class SocialsResponse(BaseModel):
    id:int
    github_profile_url:HttpUrl| None = None
    linkedin_profile_url:HttpUrl| None = None
    leetcode_profile_url:HttpUrl| None = None
    codeforces_profile_url:HttpUrl| None = None
    portfolio_profile_url:HttpUrl| None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)