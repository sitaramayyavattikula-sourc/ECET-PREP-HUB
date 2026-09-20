import os
from dotenv import load_dotenv

# Automatically load environment variables from .env file in project root
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=dotenv_path, override=True)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ecet_production_secret_key_2026_safe")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
