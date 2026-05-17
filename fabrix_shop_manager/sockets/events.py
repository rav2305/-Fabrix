from datetime import datetime

from flask_socketio import emit

from ..extensions import socketio
from ..services.dashboard_service import get_dashboard_stats


def register_socket_handlers():
    @socketio.on("connect")
    def handle_connect():
        emit(
            "socket:connected",
            {
                "success": True,
                "server_time": datetime.utcnow().isoformat(),
                "stats": get_dashboard_stats(),
            },
        )

    @socketio.on("dashboard:request")
    def handle_dashboard_request():
        emit(
            "dashboard:refresh",
            {
                "reason": "client_requested",
                "stats": get_dashboard_stats(),
                "occurred_at": datetime.utcnow().isoformat(),
            },
        )
