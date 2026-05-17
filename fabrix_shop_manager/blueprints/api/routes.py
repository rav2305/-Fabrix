from flask import Blueprint, jsonify, request
from sqlalchemy.exc import OperationalError

from ...services.billing_service import create_bill, get_bill_history
from ...services.dashboard_service import get_dashboard_stats
from ...services.inventory_service import (
    bulk_create_products,
    create_product,
    delete_product,
    get_inventory_payload,
    update_product,
    update_stock,
)
from ...utils.exceptions import AppError, ValidationError


api_bp = Blueprint("api", __name__)


@api_bp.errorhandler(AppError)
def handle_api_error(error):
    return jsonify(error.to_dict()), error.status_code


@api_bp.errorhandler(OperationalError)
def handle_operational_error(_error):
    return (
        jsonify(
            {
                "success": False,
                "message": "Database temporarily unavailable. Please retry.",
            }
        ),
        503,
    )


@api_bp.post("/inventory/add")
def add_inventory_item():
    payload = request.get_json(silent=True) or {}
    product = create_product(payload)
    return jsonify({"success": True, "product": product}), 201


@api_bp.get("/inventory")
def inventory_list_route():
    return jsonify(get_inventory_payload(search=request.args.get("search")))


@api_bp.put("/inventory/update/<int:product_id>")
def update_inventory_item(product_id):
    payload = request.get_json(silent=True) or {}
    product = update_product(product_id, payload)
    return jsonify({"success": True, "product": product})


@api_bp.delete("/inventory/delete/<int:product_id>")
def delete_inventory_item(product_id):
    product = delete_product(product_id)
    return jsonify({"success": True, "product": product})


@api_bp.post("/inventory/bulk-add")
@api_bp.post("/api/bulk_add")
def bulk_add_inventory_items():
    payload = request.get_json(silent=True)
    if payload is None:
        raise ValidationError("Request body must be JSON")
    products = bulk_create_products(payload)
    return jsonify({"success": True, "count": len(products), "products": products}), 201


@api_bp.get("/api/products")
def legacy_products_api():
    return jsonify(get_inventory_payload(search=request.args.get("search")))


@api_bp.post("/bill/create")
def create_bill_route():
    payload = request.get_json(silent=True) or {}
    invoice = create_bill(payload)
    return jsonify({"success": True, "invoice_id": invoice["id"], "invoice": invoice}), 201


@api_bp.get("/bill/history")
def bill_history_route():
    days = request.args.get("days", default=180, type=int)
    history = get_bill_history(days=days)
    return jsonify({"success": True, "history": history})


@api_bp.get("/dashboard/stats")
def dashboard_stats_route():
    return jsonify({"success": True, "stats": get_dashboard_stats()})


@api_bp.post("/stock/update")
def stock_update_route():
    payload = request.get_json(silent=True) or {}
    products = update_stock(payload)
    return jsonify({"success": True, "products": products})
