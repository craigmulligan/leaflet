from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import models
from app.depends import get_db


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
async def dashboard_get(request: Request, db: Session = Depends(get_db)):
    """
    Handler for the GET /magic endpoint with a 'token' query parameter.
    """
    user_id: str | None = request.cookies.get("user_id")

    if not user_id:
        # Not logged in.
        return RedirectResponse("/signin")

    user = db.query(models.User).filter(models.User.id==user_id).one()

    return templates.TemplateResponse(request, "dashboard.html", {"email": user.email })
