from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.models import BaseModel
from app.db import engine
from app.routes import auth 
from app.routes import dashboard
from app.config import SECRET_KEY

BaseModel.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.include_router(auth.router, prefix="/auth")
app.include_router(dashboard.router, prefix="/dashboard")
