from fastapi import FastAPI
from app.models import BaseModel
from app.db import engine
from app.routes import magic

BaseModel.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(magic.router)
