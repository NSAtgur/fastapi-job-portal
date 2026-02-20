from fastapi import FastAPI
from routes import router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")
app.include_router(router)