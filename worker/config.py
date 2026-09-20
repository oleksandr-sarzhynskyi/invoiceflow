from os import getenv

API_KEY = getenv("GEMINI_API_KEY")
MODEL = getenv("MODEL")
DATABASE_URL = getenv("DATABASE_URL")
REDIS_URL = getenv("REDIS_URL")

required = {
    "API_KEY": API_KEY,
    "MODEL": MODEL,
    "DATABASE_URL": DATABASE_URL,
    "REDIS_URL": REDIS_URL
}

for name, value in required.items():
    if not value:
        raise ValueError(f"{name} is not set in environment variables.")