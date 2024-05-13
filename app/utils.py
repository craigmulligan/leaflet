import requests
import os


def is_dev():
    return os.environ.get("ENV") != "production"


def send_email(email: str):
    pass


def get_timezone_by_ip(ip: str) -> str:
    response = requests.get(f"https://ipapi.co/{ip}/json/")
    data = response.json()
    return data.get("timezone")
