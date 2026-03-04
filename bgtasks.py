from fastapi import Depends
from database import NotificationsDB,SessionLocal
from sqlalchemy.orm import Session
from ws_manager import ConnectionManager, manager

async def notify(user_id:int, message:dict):
    db = SessionLocal()

    try:
        await manager.send_to_user(user_id, message)
    except Exception:
        pass
    notification = NotificationsDB(user_id = user_id, message = message)
    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification