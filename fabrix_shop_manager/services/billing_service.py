from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..models import Invoice, InvoiceItem, Product
from ..utils.db import run_transaction
from ..utils.decimal_utils import parse_decimal, parse_int, quantize_money
from ..utils.exceptions import NotFoundError, ValidationError
from .sync_service import broadcast_bill_created, broadcast_inventory_refresh


def create_bill(payload):
    items_data = payload.get("items") or []
    if not items_data:
        raise ValidationError("No items in the bill")

    customer_name = (payload.get("customer_name") or "").strip()
    if not customer_name:
        raise ValidationError("Customer name is required")

    def operation(session):
        product_ids = sorted(
            {parse_int(item.get("product_id"), "product_id") for item in items_data}
        )
        products = session.execute(
            select(Product)
            .where(Product.id.in_(product_ids))
            .order_by(Product.id.asc())
            .with_for_update()
        ).scalars().all()

        product_map = {product.id: product for product in products}
        if len(product_map) != len(product_ids):
            raise ValidationError("One or more selected products do not exist")

        subtotal = parse_decimal("0", "subtotal")
        total_purchase_cost = parse_decimal("0", "total_purchase_cost")
        invoice_items = []

        for raw_item in items_data:
            product_id = parse_int(raw_item.get("product_id"), "product_id")
            quantity = parse_int(raw_item.get("quantity"), "quantity")
            if quantity <= 0:
                raise ValidationError("Quantity must be greater than zero")

            product = product_map[product_id]
            if product.stock < quantity:
                raise ValidationError(f"Insufficient stock for {product.name}")

            unit_price = parse_decimal(raw_item.get("price", product.price), "price")
            line_total = quantize_money(unit_price * quantity)
            purchase_total = quantize_money(product.purchase_price * quantity)

            subtotal += line_total
            total_purchase_cost += purchase_total
            product.stock -= quantity

            invoice_items.append(
                InvoiceItem(
                    product_id=product.id,
                    product_name=product.name,
                    quantity=quantity,
                    price=unit_price,
                    purchase_price=product.purchase_price,
                    total=line_total,
                    profit=quantize_money(line_total - purchase_total),
                )
            )

        discount_percent = parse_decimal(
            payload.get("discount_percent", 0), "discount_percent"
        )
        gst_percent = parse_decimal(payload.get("gst_percent", 0), "gst_percent")
        discount_amount = quantize_money(subtotal * (discount_percent / 100))
        after_discount = quantize_money(subtotal - discount_amount)
        gst_amount = quantize_money(after_discount * (gst_percent / 100))
        total_amount = quantize_money(after_discount + gst_amount)
        total_profit = quantize_money(after_discount - total_purchase_cost)

        invoice = Invoice(
            invoice_number=_generate_invoice_number(),
            customer_name=customer_name,
            customer_phone=(payload.get("customer_phone") or "").strip() or None,
            payment_mode=(payload.get("payment_mode") or "UPI").strip(),
            subtotal=subtotal,
            discount_percent=discount_percent,
            discount_amount=discount_amount,
            gst_percent=gst_percent,
            gst_amount=gst_amount,
            total_amount=total_amount,
            total_profit=total_profit,
            items=invoice_items,
        )
        session.add(invoice)
        session.flush()
        return invoice.id

    invoice_id = run_transaction(operation)
    invoice_payload = get_invoice_payload(invoice_id)
    broadcast_inventory_refresh(
        "bill_created",
        [item["product_id"] for item in invoice_payload["items"] if item["product_id"]],
    )
    broadcast_bill_created(invoice_payload)
    return invoice_payload


def get_bill_history(days=180):
    start_date = datetime.utcnow() - timedelta(days=days)
    invoices = db.session.execute(
        select(Invoice).where(Invoice.date >= start_date).order_by(Invoice.date.desc())
    ).scalars().all()
    return [serialize_invoice_summary(invoice) for invoice in invoices]


def get_invoice_or_404(invoice_id):
    invoice = db.session.execute(
        select(Invoice)
        .options(selectinload(Invoice.items))
        .where(Invoice.id == invoice_id)
    ).scalar_one_or_none()
    if not invoice:
        raise NotFoundError("Invoice not found")
    return invoice


def get_invoice_payload(invoice_id):
    invoice = get_invoice_or_404(invoice_id)
    return serialize_invoice_detail(invoice)


def serialize_invoice_summary(invoice):
    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "date": invoice.date.isoformat(),
        "customer_name": invoice.customer_name,
        "customer_phone": invoice.customer_phone,
        "payment_mode": invoice.payment_mode,
        "subtotal": float(invoice.subtotal),
        "gst_amount": float(invoice.gst_amount),
        "discount_amount": float(invoice.discount_amount),
        "total_amount": float(invoice.total_amount),
        "total_profit": float(invoice.total_profit),
    }


def serialize_invoice_detail(invoice):
    payload = serialize_invoice_summary(invoice)
    payload.update(
        {
            "discount_percent": float(invoice.discount_percent),
            "gst_percent": float(invoice.gst_percent),
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "price": float(item.price),
                    "purchase_price": float(item.purchase_price),
                    "total": float(item.total),
                    "profit": float(item.profit),
                }
                for item in invoice.items
            ],
        }
    )
    return payload


def _generate_invoice_number():
    return f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
