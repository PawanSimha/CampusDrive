import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "devops_fallback_secret")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/campusdrive_dev")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    UPLOAD_FOLDER = "static/uploads"
