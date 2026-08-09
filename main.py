from fastapi import FastAPI
from routes.note import note
from routes.auth import user
from routes.landing import landing
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os


app = FastAPI()
app.mount("/static", StaticFiles(directory = "static"), name  = "static")

app.include_router(note)
app.include_router(user)
app.include_router(landing)


load_dotenv()
secretkey = os.getenv("SECRET_KEY")
app.add_middleware(
    SessionMiddleware,
    secret_key = secretkey)