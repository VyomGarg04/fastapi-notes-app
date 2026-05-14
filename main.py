from fastapi import FastAPI
from routes.note import note
from routes.auth import user
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory = "static"), name  = "static")

app.include_router(note)
app.include_router(user)