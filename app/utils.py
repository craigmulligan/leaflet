import os

def is_dev():
    return os.environ.get("ENV") != "production"
