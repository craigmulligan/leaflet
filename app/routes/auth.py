from fastapi import APIRouter, Request, Depends, Form, HTTPException, Query 
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from itsdangerous import BadSignature, SignatureExpired
from typing import Annotated

from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import models
from app.depends import get_db
from app.config import IS_DEV


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/magic")
def magic(request: Request, email: Annotated[str, Form()], db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).one_or_none()
    
    if user is None:
        try:
            user = models.User(email=email)
            db.add(user)
            db.commit()
            db.refresh(user)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # User is now created or present
    token = user.get_signin_token()
    magic_url = f"/auth/magic?token={token}"

    if not IS_DEV:
        ## TODO send email
        pass
        # (user.email, "Signin link", f"{HOST_URL}/{magic_path}")

    return templates.TemplateResponse(request, "dashboard.html", {"email": user.email, "magic_url": magic_url if IS_DEV else None })


@router.get("/magic")
async def magic_get(request: Request, token: str = Query(...)):
    """
    Handler for the GET /magic endpoint with a 'token' query parameter.
    """
    if not token:
        raise HTTPException(status_code=400, detail="A token is required to signin")

    try:
        user_id = models.User.verify_signin_token(token)
    except SignatureExpired:
        raise HTTPException(status_code=403, detail="Your link has expired")
    except BadSignature:
        raise HTTPException(status_code=403)

    response = RedirectResponse("/dashboard")
    response.set_cookie(key="user_id", value=user_id, httponly=True)  # Store user_id in HTTP cookie
    return response 


@router.get("/signin")
async def signin_get(request: Request):
    """
    signin form
    """
    return templates.TemplateResponse(request, "signin.html")
