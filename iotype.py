from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Dict, Any

class CreateUser(BaseModel):
    name:str
    email:str
    password:str
    role:str
    profile_pic:str| None = None
    class Config:
            model_config = ConfigDict(from_attributes=True)
    
class UserResponse(BaseModel):
    id:int
    name:str
    email:str
    role:str
    profile_pic:str| None = None
    is_active:bool

    class Config:
            model_config = ConfigDict(from_attributes=True)

class JobCreate(BaseModel):
    title:str
    company:str
    salary:int
    location:str
    job_type:str

    class Config:
        model_config = ConfigDict(from_attributes=True)

class JobResponse(BaseModel):
    id:int
    title:str
    company:str
    salary:int
    location:str
    job_type:str
    created_at:datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)


class JobApply(BaseModel):
    pass

    class Config:
        model_config = ConfigDict(from_attributes=True)


class ApplicationResponse(BaseModel):
    user_name:str
    user_id:int
    job_id:int
    status:str
    applied_at:datetime
    class Config:
        model_config = ConfigDict(from_attributes=True)

class NotificationResponse(BaseModel):
    id:int
    message:str
    created_at:datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)

class UploadResponse(BaseModel):
    image_url:str| None = None
    class Config:
        model_config = ConfigDict(from_attributes = True)