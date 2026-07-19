from models import NotificationsDB, JobsDB, UsersDB
from ws_manager import manager
import asyncio
import logging
from database import AsyncSessionLocal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

async def process_notification(data: dict):
    logger.info("process_notification called")
    logger.info(data)
    async with AsyncSessionLocal() as db:  # ← add this
        try:
            templates= {
                "application": "{user} applied for {job} at {company}",
                "job posted": "{company} is hiring for {job}",
                "activated": "Your account has been activated",
                "deactivated": "Your account has been deactivated",
                "application status updated":"Your application for {job} at {company} is {status} "
                }

            template = templates.get(data["type"])

            if not template:
                raise ValueError("Unknown notification type")            
            
            if data["type"] == "job posted":
                job_id = data["job_id"]

                result = await db.execute(select(JobsDB).where(JobsDB.id == job_id))

                job = result.scalar_one_or_none()

                logger.info("message for %s job posting", job.title)

                message = template.format(
                    company = job.company,
                    job = job.title
                )

            elif data["type"]=="application":
                user_id = data["user_id"]
                job_id = data["job_id"]

                result = await db.execute(select(UsersDB).where(UsersDB.id == user_id))
                user = result.scalar_one_or_none()

                result = await db.execute(select(JobsDB).where(JobsDB.id == job_id))
                job = result.scalar_one_or_none()

                message = template.format(
                    user = user.name,
                    job = job.title,
                    company = job.company
                )

            elif data["type"]=="activated":
                
                message = template
            
            elif data["type"]=="deactivated":
                
                message = template  
            
            elif data["type"] == "application status updated":
                message = template.format(
                    job = data["job_title"],
                    company = data["company"],
                    status = data["status"]
                )

            receiver_ids = data["receiver_id"]

        # save to DB
            if isinstance(receiver_ids, list):
                for user_id in receiver_ids:
                    notification = NotificationsDB(user_id=user_id, message=message)
                    db.add(notification)
                    await manager.send_to_user(user_id, message)
                
                await db.commit()

                    
            else:
                notification = NotificationsDB(user_id=receiver_ids, message=message)
                db.add(notification)
                await db.commit()
                await manager.send_to_user(receiver_ids, message)

        

        except Exception as e:
            logger.exception("Background_task worker failed")
            await db.rollback()
            raise 
    