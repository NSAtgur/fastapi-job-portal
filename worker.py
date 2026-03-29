from database import NotificationsDB, SessionLocal, JobsDB, UsersDB
from ws_manager import manager
import asyncio


async def process_notification(data: dict):
    print("process_notification called with:", data)  # ← add this
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

        # save to DB
        if isinstance(receiver_ids, list):
            for user_id in receiver_ids:
                notification = NotificationsDB(user_id=user_id, message=message)
                db.add(notification)
            db.commit()
        else:
            notification = NotificationsDB(user_id=receiver_ids, message=message)
            db.add(notification)
            db.commit()

        # send websocket — no threading needed, already inside event loop
        if isinstance(receiver_ids, list):
            for user_id in receiver_ids:
                await manager.send_to_user(user_id, message)
        else:
            await manager.send_to_user(receiver_ids, message)

    except Exception as e:
        print("Notification error:", e)
        db.rollback()
    finally:
        db.close()