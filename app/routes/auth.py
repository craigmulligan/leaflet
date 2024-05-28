from fastapi import (
    APIRouter,
    Request,
    Depends,
    Form,
    HTTPException,
    Query,
    BackgroundTasks,
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from itsdangerous import BadSignature, SignatureExpired
from typing import Annotated
from sqlalchemy.orm import Session

from app import mailer, models
from app.db import get_db
from app import utils

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/auth/magic")
def magic_post(
    request: Request,
    email: Annotated[str, Form()],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
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

    if utils.is_dev():
        # Send email in production.
        subject = "Leaflet Signin Link"
        body = templates.get_template("email_magic_link.html").render(
            token=token, request=request
        )
        background_tasks.add_task(mailer.mail_manager.send, email, subject, body)

    return templates.TemplateResponse(
        request,
        "magic.html",
        {"email": user.email, "magic_url": magic_url if utils.is_dev() else None},
    )


@router.get("/auth/magic")
def magic_get(token: str = Query(...), db: Session = Depends(get_db)):
    """
    Handler for the GET /magic endpoint with a 'token' query parameter.
    """
    if not token:
        raise HTTPException(status_code=400, detail="A token is required to signin")

    try:
        user_id = models.User.verify_signin_token(token)
        user = db.query(models.User).filter(models.User.id == user_id).one()
        user.is_email_confirmed = True  # Set it to whatever value you need
        db.commit()
    except SignatureExpired:
        raise HTTPException(status_code=403, detail="Your link has expired")
    except BadSignature:
        raise HTTPException(status_code=403)

    response = RedirectResponse("/dashboard")
    response.set_cookie(
        key="user_id", value=user_id, httponly=True
    )  # Store user_id in HTTP cookie
    return response


@router.get("/signin")
def signin_get(request: Request):
    """
    signin form
    """
    return templates.TemplateResponse(request, "signin.html")


@router.get("/")
def home(request: Request):
    """
    signin form
    """
    user_id: str | None = request.cookies.get("user_id")
    if not user_id:
        # Not logged in.
        return RedirectResponse("/signin")

    return RedirectResponse("/dashboard")
