from fastapi import FastAPI
from routes import router
from fastapi.middleware.cors import CORSMiddleware
import logging


app = FastAPI()

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s %(levelname)s %(name)s %(message)s"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://careerdock-app.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)