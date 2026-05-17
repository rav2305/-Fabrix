import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "secret")
    
    # Database configuration - using Railway private domain for internal connections
    MYSQLHOST = os.getenv("MYSQLHOST", "localhost")
    MYSQLPORT = os.getenv("MYSQLPORT", "3306")
    MYSQLUSER = os.getenv("MYSQLUSER", "root")
    MYSQLPASSWORD = os.getenv("MYSQLPASSWORD", "")
    MYSQLDATABASE = os.getenv("MYSQLDATABASE", "fabrix_shop_manager")
    
    # Build database URI correctly
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQLUSER}:{MYSQLPASSWORD}"
        f"@{MYSQLHOST}:{MYSQLPORT}/{MYSQLDATABASE}?charset=utf8mb4"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
    }
    
    # App configuration
    APP_HOST = "0.0.0.0"
    APP_PORT = int(os.getenv("PORT", 8080))
    DEBUG = False
    
    # SocketIO configuration
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    SOCKETIO_PING_TIMEOUT = 20
    SOCKETIO_PING_INTERVAL = 25
    
    # Inventory settings
    INVENTORY_LOW_STOCK_THRESHOLD = 10

def get_config():
    return Config
