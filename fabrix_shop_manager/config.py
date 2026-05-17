import os
from urllib.parse import quote_plus


SECRET_KEY = os.getenv("SECRET_KEY", "replace-with-a-secure-random-secret")

DB_USERNAME = os.getenv("DB_USERNAME", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "fabrix_shop_manager")

DB_POOL_RECYCLE = 1800
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_TIMEOUT = 30
DB_TRANSACTION_RETRIES = 3

SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
SOCKETIO_PING_TIMEOUT = 20
SOCKETIO_PING_INTERVAL = 25

APP_HOST = "0.0.0.0"
APP_PORT = 5000
DEBUG = False

INVENTORY_LOW_STOCK_THRESHOLD = 10

PUBLIC_BASE_URL = os.getenv(
    "PUBLIC_BASE_URL",
    "https://fabrix-x4ty.onrender.com"
)


def _build_database_uri() -> str:
    credential_part = f"{DB_USERNAME}:{quote_plus(DB_PASSWORD)}"

    return (
        f"mysql+pymysql://{credential_part}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?charset=utf8mb4"
    )


class Config:
    SECRET_KEY = SECRET_KEY
    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def get_config():
    return Config