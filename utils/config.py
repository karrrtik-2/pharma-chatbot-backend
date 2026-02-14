from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_AVAILABILITY_FILE = DATA_DIR / "doctor_availability.csv"
UPDATED_AVAILABILITY_FILE = DATA_DIR / "availability.csv"


def get_api_host() -> str:
    return os.getenv("API_HOST", "127.0.0.1")


def get_api_port() -> int:
    return int(os.getenv("API_PORT", "8003"))


def get_api_base_url() -> str:
    return os.getenv("API_BASE_URL", f"http://{get_api_host()}:{get_api_port()}")


def get_default_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o")


def get_recursion_limit() -> int:
    return int(os.getenv("RECURSION_LIMIT", "20"))


def get_active_availability_file() -> Path:
    if UPDATED_AVAILABILITY_FILE.exists():
        return UPDATED_AVAILABILITY_FILE
    return DEFAULT_AVAILABILITY_FILE
