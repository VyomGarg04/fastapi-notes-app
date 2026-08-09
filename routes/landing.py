from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates



landing = APIRouter()
templates = Jinja2Templates(directory = "templates")

@landing.get("/",response_class = HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "landing.html",
        context = {
                "request":request,
                "navbar_type":"landing"
            }
        )