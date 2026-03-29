from database import NotificationsDB, SessionLocal, JobsDB, UsersDB
from ws_manager import manager
from redis_client import redis_conn
import json
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
QUEUE_NAME = os.getenv("QUEUE_NAME")

main_loop = None  # set by main.py at startup

print("Worker started")


def process_task(data: dict):
    print("Processing task:", data)
    db = SessionLocal()
    try:
        user = None
        job = None

        if "user_id" in data:
            user = db.query(UsersDB).filter(UsersDB.id == data["user_id"]).first()

        if "job_id" in data:
            job = db.query(JobsDB).filter(JobsDB.id == data["job_id"]).first()

        if data["type"] == "application":
            message = f"{user.name} applied for {job.title} at {job.company}"

        elif data["type"] == "job posted":
            message = f"{job.company} is hiring for {job.title} at {job.location}"

        elif data["type"] == "deactivated":
            message = "Your account has been deactivated"

        elif data["type"] == "activated":
            message = "Your account has been activated"

        elif data["type"] == "job deleted":
            message = f"Job posting for {data['job_title']} at {data['job_company']} has been deleted"

        else:
            print("Unknown notification type:", data["type"])
            return

        receiver_ids = data["receiver_id"]

        # save notifications to DB
        if isinstance(receiver_ids, list):
            for user_id in receiver_ids:
                notification = NotificationsDB(user_id=user_id, message=message)
                db.add(notification)
            db.commit()
        else:
            notification = NotificationsDB(user_id=receiver_ids, message=message)
            db.add(notification)
            db.commit()
            db.refresh(notification)

        # send websocket notifications
        if main_loop and main_loop.is_running():
            if isinstance(receiver_ids, list):
                for user_id in receiver_ids:
                    asyncio.run_coroutine_threadsafe(
                        manager.send_to_user(user_id, message),
                        main_loop
                    )
            else:
                future = asyncio.run_coroutine_threadsafe(
                    manager.send_to_user(receiver_ids, message),
                    main_loop
                )
                try:
                    future.result(timeout=5)
                except Exception as e:
                    print("WebSocket delivery error:", e)
        else:
            print("Main event loop not available, skipping WebSocket push")

    finally:
        db.close()


def worker():
    while True:
        print("Waiting for Redis task...")
        tasks = redis_conn.brpop(QUEUE_NAME)
        data = json.loads(tasks[1])
        print("Received task:", data)
        process_task(data)