import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "secret")
    MYSQLHOST = os.getenv("MYSQLHOST")
    MYSQLPORT = os.getenv("MYSQLPORT")
    MYSQLUSER = os.getenv("MYSQLUSER")
    MYSQLPASSWORD = os.getenv("MYSQLPASSWORD")
    MYSQLDATABASE = os.getenv("MYSQLDATABASE")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQLUSER}:{MYSQLPASSWORD}"
        f"@{MYSQLHOST}:{MYSQLPORT}/{MYSQLDATABASE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_HOST = "0.0.0.0"
    APP_PORT = int(os.getenv("PORT", 8080))
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    SOCKETIO_PING_TIMEOUT = 20
    SOCKETIO_PING_INTERVAL = 25
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
    }

def get_config():
    return Config
