from fastapi import Depends, FastAPI, File, Request, UploadFile
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import models
from .db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/user/")
async def user_create(request: Request, email: UploadFile = File(...), db: Session = Depends(get_db)):
    email_content = await email.read()
    email_str = email_content.decode()

    new_user = models.User(email=email_str)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return templates.TemplateResponse(request, "dashboard.html", {"email": new_user.email})
