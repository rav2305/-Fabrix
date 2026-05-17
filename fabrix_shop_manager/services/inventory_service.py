from sqlalchemy import select

from ..extensions import db
from ..models import Product
from ..utils.db import run_transaction
from ..utils.decimal_utils import parse_decimal, parse_int
from ..utils.exceptions import NotFoundError, ValidationError
from .sync_service import broadcast_inventory_refresh


def list_products(search=None):
    query = select(Product).order_by(Product.name.asc(), Product.id.asc())
    if search:
        query = query.where(Product.name.ilike(f"%{search.strip()}%"))
    return db.session.execute(query).scalars().all()


def get_inventory_payload(search=None):
    return [product.to_dict() for product in list_products(search=search)]


def create_product(payload):
    def operation(session):
        product = Product(
            name=(payload.get("name") or "").strip(),
            price=parse_decimal(payload.get("price"), "price"),
            purchase_price=parse_decimal(
                payload.get("purchase_price"), "purchase_price"
            ),
            stock=parse_int(payload.get("stock", 0), "stock"),
        )
        _validate_product(product)
        session.add(product)
        session.flush()
        return product.to_dict()

    created_product = run_transaction(operation)
    broadcast_inventory_refresh("product_added", [created_product["id"]])
    return created_product


def update_product(product_id, payload):
    def operation(session):
        product = session.get(Product, product_id)
        if not product:
            raise NotFoundError("Product not found")

        product.name = (payload.get("name") or product.name).strip()
        product.price = parse_decimal(payload.get("price", product.price), "price")
        product.purchase_price = parse_decimal(
            payload.get("purchase_price", product.purchase_price), "purchase_price"
        )
        product.stock = parse_int(payload.get("stock", product.stock), "stock")
        _validate_product(product)
        session.flush()
        return product.to_dict()

    updated_product = run_transaction(operation)
    broadcast_inventory_refresh("product_updated", [updated_product["id"]])
    return updated_product


def delete_product(product_id):
    def operation(session):
        product = session.get(Product, product_id)
        if not product:
            raise NotFoundError("Product not found")
        product_data = product.to_dict()
        session.delete(product)
        return product_data

    deleted_product = run_transaction(operation)
    broadcast_inventory_refresh("product_deleted", [deleted_product["id"]])
    return deleted_product


def bulk_create_products(rows):
    if not isinstance(rows, list) or not rows:
        raise ValidationError("Bulk upload payload must contain at least one product")

    def operation(session):
        added_products = []
        for row in rows:
            product = Product(
                name=(row.get("name") or "").strip(),
                stock=parse_int(row.get("qty", row.get("stock", 0)), "qty"),
                price=parse_decimal(row.get("price"), "price"),
                purchase_price=parse_decimal(
                    row.get("purchase_price"), "purchase_price"
                ),
            )
            _validate_product(product)
            session.add(product)
            session.flush()
            added_products.append(product.to_dict())
        return added_products

    products = run_transaction(operation)
    broadcast_inventory_refresh(
        "bulk_upload_completed", [product["id"] for product in products]
    )
    return products


def update_stock(payload):
    updates = payload.get("updates")
    if not updates:
        single_product_id = payload.get("product_id")
        if single_product_id is None:
            raise ValidationError("Provide either product_id or updates")
        updates = [payload]

    normalized_updates = []
    for item in updates:
        product_id = parse_int(item.get("product_id"), "product_id")
        delta = item.get("delta")
        new_stock = item.get("stock")
        if delta is None and new_stock is None:
            raise ValidationError("Each stock update needs either delta or stock")
        normalized_updates.append(
            {
                "product_id": product_id,
                "delta": parse_int(delta, "delta") if delta is not None else None,
                "stock": parse_int(new_stock, "stock") if new_stock is not None else None,
            }
        )

    normalized_updates.sort(key=lambda item: item["product_id"])

    def operation(session):
        product_ids = [item["product_id"] for item in normalized_updates]
        products = session.execute(
            select(Product)
            .where(Product.id.in_(product_ids))
            .order_by(Product.id.asc())
            .with_for_update()
        ).scalars().all()

        product_map = {product.id: product for product in products}
        if len(product_map) != len(set(product_ids)):
            raise NotFoundError("One or more products were not found")

        updated_products = []
        for item in normalized_updates:
            product = product_map[item["product_id"]]
            if item["stock"] is not None:
                product.stock = item["stock"]
            else:
                product.stock += item["delta"]

            if product.stock < 0:
                raise ValidationError(f"Stock cannot be negative for {product.name}")

            session.flush()
            updated_products.append(product.to_dict())

        return updated_products

    updated_products = run_transaction(operation)
    broadcast_inventory_refresh(
        "stock_updated", [product["id"] for product in updated_products]
    )
    return updated_products


def _validate_product(product):
    if not product.name:
        raise ValidationError("Product name is required")
    if product.price < 0:
        raise ValidationError("Selling price cannot be negative")
    if product.purchase_price < 0:
        raise ValidationError("Purchase price cannot be negative")
    if product.stock < 0:
        raise ValidationError("Stock cannot be negative")
