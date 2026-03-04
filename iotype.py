from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Dict, Any

class CreateUser(BaseModel):
    email:str
    password:str
    role:str
    
class UserResponse(BaseModel):
    id:int
    email:str
    role:str
    is_active:bool

    class Config:
            model_config = ConfigDict(from_attributes=True)

class JobCreate(BaseModel):
    title:str
    company:str

    class Config:
        model_config = ConfigDict(from_attributes=True)

class JobResponse(BaseModel):
    id:int
    title:str
    company:str
    created_at:datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)


class JobApply(BaseModel):
    pass
   
    class Config:
        model_config = ConfigDict(from_attributes=True)


class ApplicationResponse(BaseModel):
    user_id:int
    job_id:int
    status:str
    applied_at:datetime
    class Config:
        model_config = ConfigDict(from_attributes=True)

class NotificationResponse(BaseModel):
    id:int
    message:Dict[str,Any]
    created_at:datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)