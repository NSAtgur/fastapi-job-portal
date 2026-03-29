from fastapi import FastAPI
from routes import router
from fastapi.middleware.cors import  CORSMiddleware
import asyncio
from worker import worker

app = FastAPI()

origins = ["https://careerdock-app.vercel.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # allow frontend requests
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

@app.on_event("startup")
async def start_worker():
    asyncio.create_task(worker())