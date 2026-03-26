from fastapi import Depends
from database import NotificationsDB,SessionLocal, JobsDB
from sqlalchemy.orm import Session
from ws_manager import ConnectionManager, manager
from auth import get_user

async def notify(receiver_id:int, message:dict):
    db = SessionLocal()
    user = get_user(message["user_id"])
    job = db.query(JobsDB).filter(JobsDB.id == message["job_id"]).first()

    if message["type"] == "application":

        message = f"{user.id} applied for {job.title} at {job.company}"

    elif message["type"] == "job posted":
        message = f"{job.company} is hiring for {job.title} at {job.location}"
    
    elif message["type"] == "deactivated":
        message = f"Your account has been deactivated"

    elif message["type"] == "activated":
        message = f"Your account has been activated"

    try:
        await manager.send_to_user(receiver_id, message)
    except Exception:
        pass
    notification = NotificationsDB(user_id = receiver_id, message = message)
    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification