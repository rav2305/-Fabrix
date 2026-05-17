from pathlib import Path

from flask import Flask, jsonify, render_template, request

from .blueprints.api.routes import api_bp
from .blueprints.web.routes import web_bp
from .config import get_config
from .extensions import init_extensions
from .sockets.events import register_socket_handlers
from .utils.exceptions import AppError


def create_app(config_object=None):
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )
    app.config.from_object(config_object or get_config())

    init_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_socket_handlers()

    return app


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        if error.as_json:
            response = jsonify(error.to_dict())
            response.status_code = error.status_code
            return response
        return error.message, error.status_code

    @app.errorhandler(404)
    def handle_not_found(_error):
        if _wants_json_error():
            return jsonify({"success": False, "message": "Resource not found"}), 404
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def handle_server_error(_error):
        if _wants_json_error():
            return jsonify({"success": False, "message": "Internal server error"}), 500
        return render_template("500.html"), 500


def _wants_json_error():
    accept_header = request.headers.get("Accept", "").lower()
    if request.path.startswith(("/bill", "/dashboard", "/stock", "/api/")):
        return True
    if request.path.startswith("/inventory"):
        return request.method != "GET" or "application/json" in accept_header
    return "application/json" in accept_header
