from fastapi import APIRouter, Request, Depends, UploadFile, File
from fastapi.templating import Jinja2Templates

from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import models
from app.depends import get_db


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/magic/")
async def magic(request: Request, email: UploadFile = File(...), db: Session = Depends(get_db)):
    email_content = await email.read()
    email_str = email_content.decode()

    new_user = models.User(email=email_str)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return templates.TemplateResponse(request, "dashboard.html", {"email": new_user.email})

