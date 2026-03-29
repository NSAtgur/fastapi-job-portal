from fastapi import Depends
from database import NotificationsDB,SessionLocal, JobsDB, UsersDB
from sqlalchemy.orm import Session
from ws_manager import ConnectionManager, manager
from auth import get_user
from redis_client import redis_conn
import json
import time
import redis
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()
QUEUE_NAME =os.getenv("QUEUE_NAME")

def process_task(data:dict):
    db = SessionLocal()
    try:
        if "user_id" in data:    ## user_id for mentioning details in the name 
            user= db.query(UsersDB).filter(UsersDB.id == data["user_id"]).first()
    
        if "job_id" in data:
            job = db.query(JobsDB).filter(JobsDB.id == data["job_id"]).first()

        if data["type"] == "application":

            message = f"{user.id} applied for {job.title} at {job.company}"

        elif data["type"] == "job posted":
            message = f"{job.company} is hiring for {job.title} at {job.location}"
    
        elif data["type"] == "deactivated":
            message = f"Your account has been deactivated"

        elif data["type"] == "activated":
            message = f"Your account has been activated"
        
        elif data["type"] == "job deleted":
            message = f"Job posting for {job.title} at {job.company} has been deleted"

        notification = NotificationsDB(user_id = data["receiver_id"], message = message)  
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        try:
            asyncio.run(manager.send_to_user(data["receiver_id"], message))
        except Exception as e:
            print("WebSocket error:", e)
        
        return notification
    
    finally:
        db.close()


def worker():
    while True:
        tasks = redis_conn.brpop(QUEUE_NAME)
        data = json.loads(tasks[1])
        process_task(data)
        

