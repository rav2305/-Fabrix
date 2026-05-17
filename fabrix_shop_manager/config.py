from urllib.parse import quote_plus

# Centralized in-code settings.
# Edit these values directly when moving the project to a different machine/server.
SECRET_KEY = "replace-with-a-secure-random-secret"
DB_USERNAME = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "fabrix_shop_manager"
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
PUBLIC_BASE_URL = "https://fabrix-x4ty.onrender.com"

def _build_database_uri() -> str:
    return "sqlite:///fabrix.db"


class Config:
    SECRET_KEY = SECRET_KEY
    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def get_config():
    return Config
