from fabrix_shop_manager import create_app
from fabrix_shop_manager.extensions import socketio


app = create_app()


if __name__ == "__main__":
    socketio.run(
        app,
        host=app.config["APP_HOST"],
        port=app.config["APP_PORT"],
        debug=app.config["DEBUG"],
    )
