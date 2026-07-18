from sqlalchemy.ext.asyncio import(
        create_async_engine,
        AsyncSession,
        async_sessionmaker
    )
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import AsyncGenerator


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,        # ← reduce from 5
    max_overflow=10,     # ← reduce from 10
    pool_recycle=300,   # ← recycle connections every 5 mins
    pool_timeout=30
)

class Base(DeclarativeBase):
    pass

AsyncSessionLocal = async_sessionmaker(
    autoflush=False,
    bind=engine,
    expire_on_commit= False,
)


async def get_db() -> AsyncGenerator[AsyncSession,None]:

    async with AsyncSessionLocal() as session:
        yield session

        



    
