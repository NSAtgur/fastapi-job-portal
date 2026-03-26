from fastapi import Depends
from database import NotificationsDB,SessionLocal, JobsDB, UsersDB
from sqlalchemy.orm import Session
from ws_manager import ConnectionManager, manager
from auth import get_user

async def notify(receiver_id:int, data:dict):
    db = SessionLocal()
    if "user_id" in data:
        user= db.query(UsersDB).filter(UsersDB.id == data["user_id"]).first()
    
    if "job_id" in data:
        job = db.query(JobsDB).filter(JobsDB.id == data["job_id"]).first()
        print(" notify triggered for job:", job.id)
    if data["type"] == "application":

        message = f"{user.id} applied for {job.title} at {job.company}"

    elif data["type"] == "job posted":
        message = f"{job.company} is hiring for {job.title} at {job.location}"
    
    elif data["type"] == "deactivated":
        message = f"Your account has been deactivated"

    elif data["type"] == "activated":
        message = f"Your account has been activated"

    try:
        await manager.send_to_user(receiver_id, message)
    except Exception as e:
        print("WebSocket error:", e)

    notification = NotificationsDB(user_id = receiver_id, message = message)
    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification