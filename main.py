from dotenv import load_dotenv
import os

load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from routes.note import note
from routes.auth import user
from routes.landing import landing


app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

app.include_router(note)
app.include_router(user)
app.include_router(landing)

secretkey = os.getenv("SECRET_KEY")

if not secretkey:
    raise ValueError("SECRET_KEY is not configured")

app.add_middleware(
    SessionMiddleware,
    secret_key=secretkey
)