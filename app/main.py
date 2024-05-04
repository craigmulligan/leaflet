from fastapi import FastAPI

from app.models import BaseModel
from app.db import engine
from app.routes import auth 
from app.routes import dashboard

BaseModel.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(auth.router, prefix="/auth")
app.include_router(dashboard.router, prefix="/dashboard")
