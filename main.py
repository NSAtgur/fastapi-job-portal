from fastapi import FastAPI
from routes import router
from fastapi.middleware.cors import  CORSMiddleware
from worker import worker
import threading 
import worker as worker_module
import asyncio


app = FastAPI()

print("app started")

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
def startup_event():
    print("Starting the thread")
    worker_module.main_loop = asyncio.get_event_loop()
    threading.Thread(target=worker, daemon=True).start()