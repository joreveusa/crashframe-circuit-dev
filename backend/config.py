# CrashFrame Circuit Backend API

import json
import os
from pathlib import Path
from datetime import timedelta

# Determine the directory where this file lives so we can find config.json
_BASE_DIR = Path(__file__).parent.resolve()
_CONFIG_PATH = _BASE_DIR / "config.json"


def load_config() -> dict:
    """Load configuration from config.json.  Raises FileNotFoundError if missing."""
    if not _CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"config.json not found at {_CONFIG_PATH}. "
            "Copy config.json.example and fill in your values."
        )
    with open(_CONFIG_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


# Load once at import time so all modules share the same dict
_cfg = load_config()


class Config:
    """Flask application configuration derived from config.json."""

    # -------------------------------------------------------------------
    # Database
    # -------------------------------------------------------------------
    SQLALCHEMY_DATABASE_URI: str = _cfg.get("DATABASE_URL", "sqlite:///crashframe.db")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # -------------------------------------------------------------------
    # JWT
    # -------------------------------------------------------------------
    JWT_SECRET_KEY: str = _cfg.get(
        "JWT_SECRET_KEY", "change-me-in-production-use-a-long-random-string"
    )
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(
        hours=int(_cfg.get("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 24))
    )

    # -------------------------------------------------------------------
    # Flask
    # -------------------------------------------------------------------
    DEBUG: bool = bool(_cfg.get("DEBUG", False))
    TESTING: bool = False

    # -------------------------------------------------------------------
    # CORS
    # -------------------------------------------------------------------
    CORS_ORIGINS: list = _cfg.get(
        "CORS_ORIGINS",
        ["http://localhost:3000", "http://localhost:5173"],
    )
