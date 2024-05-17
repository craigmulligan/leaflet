import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])

SECRET_KEY = "so-secret"
HOST_URL = "http://localhost:8080"
LLM_KEY = os.environ.get("LLM_KEY", "ollama")
LLM_HOST = os.environ.get("LLM_HOST", "http://localhost:11434/v1/")

MAIL_HOST = os.environ.get("MAIL_HOST", "")
MAIL_PORT = int(os.environ.get("MAIL_PORT", 465))
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
MAIL_FROM = os.environ.get("MAIL_FROM", "")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"
