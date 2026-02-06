from pydantic import BaseModel
from datetime import datetime
class CreateUser(BaseModel):
    email:str
    password:str
    role:str
    
class UserResponse(BaseModel):
    email:str
    role:str

    class Config:
        orm_mode = True

class JobCreate(BaseModel):
    title:str
    company:str

    class Config:
        orm_mode = True

class JobResponse(BaseModel):
    title:str
    company:str
    created_at:datetime

    class Config:
        orm_mode = True


class JobApply(BaseModel):
    pass
   
    class Config:
        orm_mode = True


class ApplicationResponse(BaseModel):
    user_id:int
    job_id:int
    status:str
    applied_at:datetime
    class Config:
        orm_mode = True