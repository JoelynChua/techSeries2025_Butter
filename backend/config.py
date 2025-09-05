import os

class Settings:
    # Allow overriding from env; defaults to your dev frontend
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    SWAGGER = {
        "title": "API",
        "uiversion": 3
    }
