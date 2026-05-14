from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import starlette.status as status
from config.db import conn
from utils.security import create_hash
from schemas.user import userEntity, usersEntity


user = APIRouter()
templates = Jinja2Templates(directory="templates")
user_collection = conn.notes.users


@user.get("/signup", response_class = HTMLResponse)
async def user_signup(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="signup.html",
        context = {
            "request": request,
            "show_navbar": False,
            "use_container": False

        }
    )

@user.post("/signup")
async def create_user(request: Request):
    form = await request.form()
    formDict = dict(form)

    username = formDict.get("username")
    email = formDict.get("email")
    password = formDict.get("password")
    confirm_password = formDict.get("confirm_password")
    print(password)
    print(type(password))
    email = email.lower()

    if password != confirm_password:
        return RedirectResponse(url = "/signup?error=PasswordMismatch", status_code=status.HTTP_303_SEE_OTHER)
    if not email:
        return RedirectResponse(url="/signup?error=MissingEmail",status_code=status.HTTP_303_SEE_OTHER)
    
    existing_user = user_collection.find_one({"email":email})
    if existing_user:
        return RedirectResponse(url="/signup?error=EmailExists",status_code=status.HTTP_303_SEE_OTHER)
    

    hashed_password = create_hash(password)

    new_user = {
        "username":formDict["username"],
        "email": formDict["email"],
        "password": hashed_password

    }
    user_collection.insert_one(new_user)
    return RedirectResponse(url = "/login?msg=AccountCreated", status_code=status.HTTP_303_SEE_OTHER)
    