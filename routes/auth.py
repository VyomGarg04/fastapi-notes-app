from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import starlette.status as status
from config.db import conn
from utils.security import create_hash, verify_password
from schemas.user import userEntity, usersEntity


user = APIRouter()
templates = Jinja2Templates(directory="templates")
user_collection = conn.notes.users

#SIGNUP
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
    user_name = formDict.get("user_name")
    email = formDict.get("email")
    password = formDict.get("password")
    confirm_password = formDict.get("confirm_password")
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
        "user_name":formDict["user_name"],
        "email": formDict["email"].lower(),
        "password": hashed_password
    }
    user_collection.insert_one(new_user)
    return RedirectResponse(url = "/login?msg=AccountCreated", status_code=status.HTTP_303_SEE_OTHER)



#LOGIN
@user.get("/login", response_class = HTMLResponse)
async def user_login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context = {
            "request": request,
            "show_navbar": False,
            "use_container": False

        }
    )

@user.post("/login")
async def check_user(request: Request):
    form = await request.form()
    formDict = dict(form)

    email = formDict.get("email")
    password = formDict.get("password")

    if not email:
        return RedirectResponse(url="/login?error=MissingEmail",status_code=status.HTTP_303_SEE_OTHER)
    
    email = email.lower()
    user = user_collection.find_one({"email":email})
    if not user:
        return RedirectResponse(url="/login?error=InvalidCredentials",status_code=status.HTTP_303_SEE_OTHER)
    stored_hash  = user["password"]

    user_exists = verify_password(password, stored_hash)
    if user_exists:
        request.session["user"] = email
        request.session["user_id"] = str(user["_id"])
        request.session["user_name"] = user["user_name"]
        return RedirectResponse(url = "/notes", status_code=status.HTTP_303_SEE_OTHER)
    else:
        return RedirectResponse(url = "/login?msg=LoginUnsuccessful", status_code=status.HTTP_303_SEE_OTHER)
    


#LOGOUT
@user.get("/logout", response_class = HTMLResponse)
async def user_login(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)