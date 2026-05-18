import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///device_farm.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))

    APPIUM_HOST = os.getenv("APPIUM_HOST", "localhost")
    APPIUM_BASE_PORT = int(os.getenv("APPIUM_BASE_PORT", 4723))
    APPIUM_MAX_SESSIONS = int(os.getenv("APPIUM_MAX_SESSIONS", 5))

    MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", 50))
    SESSION_TIMEOUT_SECONDS = int(os.getenv("SESSION_TIMEOUT_SECONDS", 300))

    ADB_PATH = os.getenv("ADB_PATH", "adb")
    ADB_CONNECT_TIMEOUT = int(os.getenv("ADB_CONNECT_TIMEOUT", 10))

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    CORS_ORIGINS = [FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"]
