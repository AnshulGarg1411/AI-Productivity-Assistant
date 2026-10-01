from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")


class Settings:

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    SESSION_SECRET = os.getenv("SESSION_SECRET")

    JWT_SECRET = os.getenv("JWT_SECRET")

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:anshulgarg@localhost/productivity"
    )

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # AI features (task extraction, morning brief narration) are only
    # attempted when a key is actually present -- the app must keep working
    # perfectly for anyone running it without a GROQ key.
    AI_FEATURES_ENABLED = bool(GROQ_API_KEY := os.getenv("GROQ_API_KEY")    )

    GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


settings = Settings()