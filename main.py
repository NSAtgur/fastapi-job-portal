from fastapi import FastAPI
from routes import router
from fastapi.middleware.cors import CORSMiddleware
from worker import worker
import threading
import asyncio
import worker as worker_module


app = FastAPI()

print("app started")

origins = ["https://careerdock-app.vercel.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    print("Starting the thread")
    worker_module.main_loop = asyncio.get_event_loop()  # capture main event loop
    threading.Thread(target=worker, daemon=True).start()