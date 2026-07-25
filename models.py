from sqlalchemy import Integer, String, ForeignKey, DateTime, UniqueConstraint, Boolean
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import mapped_column, relationship, Mapped
from datetime import datetime,timezone
from database import Base
from schemas import ApplicationStatus, JobStatus



class UsersDB(Base):
    """

    Represents a user registered on the platform

    Saves authentication details and basic info about the user i.e. name, email, profile_pic url,
    bio, headline, experience_years, education.
    It also store the info about the acitvity of the user's account (is_active, is_verified)
    
    """

    __tablename__ = "users"

    id:Mapped[int] = mapped_column(Integer, primary_key=True, index= True)
    name:Mapped[str] = mapped_column(String(15), unique = True, nullable = False)
    email:Mapped[str] = mapped_column(String(255), unique = True, nullable = False)
    password:Mapped[str] = mapped_column(String(200), nullable= False)
    role:Mapped[str] = mapped_column(String,nullable= False)
    is_active:Mapped[bool] = mapped_column(Boolean, default= True)
    is_verified:Mapped[bool] = mapped_column(Boolean, default = False, nullable=True)
    profile_pic:Mapped[str] = mapped_column(String(255), nullable= True)
    experience_years:Mapped[int] = mapped_column(Integer, nullable= True)
    bio:Mapped[str] = mapped_column(String(500), nullable= True)
    headline:Mapped[str] = mapped_column(String(500), nullable= True)
    education:Mapped[str] = mapped_column(String(50), nullable=True)
    created_at:Mapped[datetime] = mapped_column(DateTime, default= datetime.utcnow)


    projects = relationship("Projects", back_populates="user")
    applications = relationship("ApplicationsDB", back_populates='user')
    jobs = relationship("JobsDB", back_populates ='creator')
    notifications = relationship("NotificationsDB", back_populates="user")
    experiences = relationship("Experience", back_populates="user")
    userskills = relationship("UserSkills", back_populates="user")
    socials = relationship("Socials", back_populates="user")

class Projects(Base):
    """ 
    Stores the project info of the registered user.
    Contains columns to store project title, description, github_link and live application link
    
    """
    __tablename__="projects"

    id:Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id:Mapped[int] = mapped_column(Integer,ForeignKey("users.id"), nullable= False, index= True)
    title:Mapped[str] = mapped_column(String(30), nullable= True)
    description:Mapped[str] = mapped_column(String(100), nullable= True)
    github_link:Mapped[str] = mapped_column(String(255), nullable= True)
    live_url:Mapped[str] = mapped_column(String(255), nullable= True)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                    default=lambda: datetime.now(timezone.utc))

    user = relationship("UsersDB", back_populates= "projects")
    
    __table_args__ = (UniqueConstraint("user_id", "github_link", name = "unique_user_project"),)


class Experience(Base):
    """
    Store the info about the experience of user.
    Columns are for organization user worked in, the start and end dates, role, contributions,
    skills used during the time period, whether or not the user is currently working at the organization.

    """
    __tablename__ = "experiences"

    id:Mapped[int] = mapped_column(Integer, primary_key= True, index = True)
    user_id:Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index= True)
    organization_name:Mapped[str] = mapped_column(String(100), nullable = True)
    role:Mapped[str] = mapped_column(String(100), nullable = True)
    start_date:Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable = True)
    end_date:Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable = True)
    contribution:Mapped[str] = mapped_column(String(500), nullable= True)
    currently_working:Mapped[bool] = mapped_column(Boolean, default = True)
    skills_used:Mapped[str] = mapped_column(String(100), nullable = True)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                    default=lambda: datetime.now(timezone.utc))
    
    user = relationship("UsersDB", back_populates= "experiences")


class Skills(Base): 
    """
    Stores the skills entered by the registered users.
    """

    __tablename__ = "skills"
    
    id:Mapped[int] = mapped_column(Integer, primary_key= True)
    skill_name:Mapped[str] = mapped_column(String(20), unique = True)

    userskills = relationship("UserSkills", back_populates="skills")


class UserSkills(Base):
    """
    Stores the skill_ids of the respective registered user.
    """

    __tablename__ = "userskills"

    id:Mapped[int] = mapped_column(Integer, primary_key= True)
    user_id:Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    skill_id:Mapped[int] = mapped_column(Integer, ForeignKey("skills.id"))
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                    default=lambda: datetime.now(timezone.utc))

    user = relationship("UsersDB", back_populates="userskills")
    skills = relationship("Skills", back_populates="userskills")

    __table_args__= (UniqueConstraint("user_id", "skill_id", name = "unique_user_skills"),)


class JobsDB(Base):
    """
    Stores info about the jobs posted by recruiters.
    Contains- title, company, location, salary, job_type, id of recruiter who posted the respective job,
    and time stamp of the post creation.
    
    """
    __tablename__= "jobs"
    id:Mapped[int] = mapped_column(Integer, primary_key = True)
    title:Mapped[str] = mapped_column(String(20), nullable = False)
    company:Mapped[str] = mapped_column(String(30), nullable = False)
    salary:Mapped[int] = mapped_column(Integer,nullable=True)
    location:Mapped[str] = mapped_column(String(100),nullable=True)
    job_type:Mapped[str] = mapped_column(String(20),nullable=True)
    status: Mapped[str] = mapped_column(
                                    String(30),
                                    default=JobStatus.open.value,
                                    nullable=False
                                    )   
    requirements:Mapped[str] = mapped_column(String(1000), nullable=True)
    created_by:Mapped[int] = mapped_column(Integer,ForeignKey("users.id"),nullable = False)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                default=lambda: datetime.now(timezone.utc))

    creator = relationship("UsersDB", back_populates="jobs")
    applications = relationship("ApplicationsDB", back_populates= 'job')


class ApplicationsDB(Base):
    """
    Stores details about applications of users for respective job postings.
    Contains application_ids, applicant's id, job_id, timestamp of application, status of application.
    """
    __tablename__ = 'applications'
    id:Mapped[int] = mapped_column(Integer,primary_key= True)
    user_name:Mapped[str] = mapped_column(String(20),nullable=True)
    user_id:Mapped[int] = mapped_column( Integer, ForeignKey("users.id"))
    job_id:Mapped[int] = mapped_column( Integer, ForeignKey("jobs.id"))
    applied_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                        default=lambda: datetime.now(timezone.utc))
    status: Mapped[str] = mapped_column(
                                String(30),
                                default=ApplicationStatus.pending.value,
                                nullable=False,
                            )

    user = relationship("UsersDB", back_populates='applications')
    job = relationship("JobsDB", back_populates = 'applications')
    
    __table_args__= (UniqueConstraint("user_id","job_id", name ="unique_user_job"),)
    

class Socials(Base):
    """
    Stores URLs of profile links of platforms- GitHub, Linkedin, Leetcode, codeforces.
    Also it stores portfolio website link.
    """

    __tablename__ = "socials"
    
    id:Mapped[int] = mapped_column(Integer, primary_key= True)
    user_id:Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index = True)
    github_profile_url:Mapped[str] = mapped_column(String(255),nullable=True)
    linkedin_profile_url:Mapped[str] = mapped_column(String(255),nullable=True)
    leetcode_profile_url:Mapped[str] = mapped_column(String(255),nullable=True)
    codeforces_profile_url:Mapped[str] = mapped_column(String(255),nullable=True)
    portfolio_profile_url:Mapped[str] = mapped_column(String(255),nullable=True)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                    default=lambda: datetime.now(timezone.utc))


    user = relationship("UsersDB", back_populates="socials")


class NotificationsDB(Base):
    """
    Stores the notification related information which includes text, user_id, status, timestamp.
    """
    __tablename__ = 'notifications'
    id:Mapped[int] = mapped_column(Integer, primary_key = True)
    user_id:Mapped[int] = mapped_column( Integer, ForeignKey("users.id"), index = True)
    message:Mapped[str] = mapped_column(String)
    is_read:Mapped[bool] = mapped_column(Boolean, default = False)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                            default=lambda: datetime.now(timezone.utc))

    user = relationship("UsersDB", back_populates="notifications")