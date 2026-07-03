from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql://root:123456@127.0.0.1:3306/yuxiaotu_book",
    )
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-in-production-32chars")
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "168"))
    GUEST_VIDEO_PREVIEW_SECONDS: int = int(os.getenv("GUEST_VIDEO_PREVIEW_SECONDS", "180"))
    CORS_ORIGINS: List[str] = [
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS", "http://localhost:5188,http://127.0.0.1:5188"
        ).split(",")
        if o.strip()
    ]
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", os.path.join(os.getcwd(), "uploads"))


settings = Settings()
