from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.models import BaseModel
from app.db import engine
from app.routes import auth 
from app.routes import dashboard

BaseModel.metadata.create_all(bind=engine)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# unauthenticated routes
app.include_router(auth.router)

# authenticated routes
app.include_router(dashboard.router, prefix="/dashboard")
