from fastapi import APIRouter, Request, Depends, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates

from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import models
from app.depends import get_db
from app.config import HOST_URL, IS_DEV


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/magic/")
def magic(request: Request, email: UploadFile = File(...), db: Session = Depends(get_db)):
    email_content = email.file.read()
    email_str = email_content.decode()

    user = db.query(models.User).filter(models.User.email == email_str).one_or_none()
    
    if user is None:
        try:
            user = models.User(email=email_str)
            db.add(user)
            db.commit()
            db.refresh(user)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # User is now created or present
    token = user.get_signin_token()
    magic_path = f"/magic?token={token}"
    magic_markup = None

    if IS_DEV:
        magic_markup = f"<a href={magic_path}>Click here to signin.</a>"
    else:
        pass
        ## TODO send email
        # (user.email, "Signin link", f"{HOST_URL}/{magic_path}")

    return templates.TemplateResponse(request, "dashboard.html", {"email": user.email, "magic_markup": magic_markup })

