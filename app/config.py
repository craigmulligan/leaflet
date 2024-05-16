import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = "so-secret"
HOST_URL = "http://localhost:8080"
LLM_KEY = os.environ.get("LLM_KEY", "ollama")
LLM_HOST = os.environ.get("LLM_HOST", "http://localhost:11434/v1/")
