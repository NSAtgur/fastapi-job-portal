from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, DateTime, UniqueConstraint, Boolean,JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=2,        # ← reduce from 5
    max_overflow=3,     # ← reduce from 10
    pool_recycle=300,   # ← recycle connections every 5 mins
    pool_timeout=30
)
Base = declarative_base()
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class UsersDB(Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    name = Column(String,nullable=True)
    email = Column(String, unique = True, index =True)
    password = Column(String)
    profile_pic = Column(String,nullable = True)
    profile_pic_public_id = Column(String, nullable = True)
    role = Column(String, default = "user", nullable = False)
    is_active = Column(Boolean, default = True)

    applications = relationship("ApplicationsDB", back_populates='user')
    jobs = relationship("JobsDB", back_populates ='creator')
    notifications = relationship("NotificationsDB", back_populates="user")

class JobsDB(Base):

    __tablename__= "jobs"
    id = Column(Integer, primary_key = True)
    title = Column(String, nullable = False)
    company = Column(String, nullable = False)
    salary = Column(Integer,nullable=True)
    location = Column(String,nullable=True)
    job_type =Column(String,nullable=True)
    created_by = Column(Integer,ForeignKey("users.id"),nullable = False)
    created_at = Column(DateTime, default = datetime.utcnow())

    creator = relationship("UsersDB", back_populates="jobs")
    applications = relationship("ApplicationsDB", back_populates= 'job')


class ApplicationsDB(Base):

    __tablename__ = 'applications'
    id = Column(Integer,primary_key= True)
    user_name = Column(String,nullable=True)
    user_id = Column( Integer, ForeignKey("users.id"))
    job_id = Column( Integer, ForeignKey("jobs.id"))
    applied_at = Column(DateTime,default = datetime.utcnow())
    status = Column( String, nullable = False)

    user = relationship("UsersDB", back_populates='applications')
    job = relationship("JobsDB", back_populates = 'applications')
    
    __table_args__= (UniqueConstraint("user_id","job_id", name ="unique_user_job"),)
    


class NotificationsDB(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key = True)
    user_id = Column( Integer, ForeignKey("users.id"), index = True)
    message = Column(String)
    is_read = Column(Boolean, default = False)
    created_at = Column(DateTime, default = datetime.utcnow())

    user = relationship("UsersDB", back_populates="notifications")

Base.metadata.create_all(engine)

Session = sessionmaker(bind = engine)

def get_db():
    db = Session()

    try:
        yield db

    finally:
        db.close()



    
