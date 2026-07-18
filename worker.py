from models import NotificationsDB, JobsDB, UsersDB
from ws_manager import manager
import asyncio
import logging
from database import AsyncSessionLocal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

async def process_notification(data: dict):
    print("process_notification called with:", data)
    async with AsyncSessionLocal as db:  # ← add this
        try:
            user = None
            job = None

            if "user_id" in data:
                result = await db.execute(select(UsersDB).where(UsersDB.id == data["user_id"]))
                user = result.scalar_one_or_none()

            if "job_id" in data:
                result = await db.execute(select(JobsDB).where(JobsDB.id == data["job_id"]))
                job = result.scalar_one_or_none()

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
                    await db.commit()
            else:
                notification = NotificationsDB(user_id=receiver_ids, message=message)
                db.add(notification)
                await db.commit()

        # send websocket — no threading needed, already inside event loop
            if isinstance(receiver_ids, list):
                for user_id in receiver_ids:
                    await manager.send_to_user(user_id, message)
            else:
                await manager.send_to_user(receiver_ids, message)

        except Exception as e:
            logger.exception("Background_task worker failed")
            await db.rollback()
        
        finally:
            await db.close()