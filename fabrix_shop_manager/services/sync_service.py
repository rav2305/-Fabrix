from datetime import datetime

from ..extensions import socketio
from .dashboard_service import get_dashboard_stats


def broadcast_inventory_refresh(reason, product_ids=None):
    socketio.emit(
        "inventory:refresh",
        {
            "reason": reason,
            "product_ids": product_ids or [],
            "occurred_at": datetime.utcnow().isoformat(),
        },
    )
    broadcast_dashboard_refresh(reason)


def broadcast_dashboard_refresh(reason):
    socketio.emit(
        "dashboard:refresh",
        {
            "reason": reason,
            "stats": get_dashboard_stats(),
            "occurred_at": datetime.utcnow().isoformat(),
        },
    )


def broadcast_bill_created(invoice_payload):
    socketio.emit(
        "bill:created",
        {
            "reason": "bill_created",
            "invoice": invoice_payload,
            "occurred_at": datetime.utcnow().isoformat(),
        },
    )
