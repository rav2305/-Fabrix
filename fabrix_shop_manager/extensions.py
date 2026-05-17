from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(session_options={"expire_on_commit": False})
migrate = Migrate(compare_type=True)
socketio = SocketIO(async_mode="threading")


def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db, directory="migrations")
    socketio.init_app(
        app,
        cors_allowed_origins=app.config["SOCKETIO_CORS_ALLOWED_ORIGINS"],
        ping_timeout=app.config["SOCKETIO_PING_TIMEOUT"],
        ping_interval=app.config["SOCKETIO_PING_INTERVAL"],
    )
