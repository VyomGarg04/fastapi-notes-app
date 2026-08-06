from fastapi import Request
from fastapi.responses import RedirectResponse

def get_current_user(request: Request):
    current_user = request.session.get("user")
    if current_user:
        return current_user
    else:
        return None