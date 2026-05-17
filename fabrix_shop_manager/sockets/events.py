from datetime import datetime

from flask_socketio import emit

from ..extensions import socketio
from ..services.dashboard_service import get_dashboard_stats


def register_socket_handlers():
    @socketio.on("connect")
    def handle_connect(auth=None):
        try:
            stats = get_dashboard_stats()
        except Exception as e:
            print(f"Warning: Could not fetch dashboard stats: {e}")
            stats = {
                "total_products": 0,
                "total_stock": 0,
                "today_sales": 0,
                "today_profit": 0,
                "as_of": datetime.utcnow().isoformat(),
            }
        
        emit(
            "socket:connected",
            {
                "success": True,
                "server_time": datetime.utcnow().isoformat(),
                "stats": stats,
            },
        )

    @socketio.on("dashboard:request")
    def handle_dashboard_request():
        try:
            stats = get_dashboard_stats()
        except Exception as e:
            print(f"Warning: Could not fetch dashboard stats: {e}")
            stats = {
                "total_products": 0,
                "total_stock": 0,
                "today_sales": 0,
                "today_profit": 0,
                "as_of": datetime.utcnow().isoformat(),
            }
        
        emit(
            "dashboard:refresh",
            {
                "reason": "client_requested",
                "stats": stats,
                "occurred_at": datetime.utcnow().isoformat(),
            },
        )
