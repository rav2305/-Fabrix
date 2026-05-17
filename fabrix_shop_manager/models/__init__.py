from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric

from ..extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class Product(TimestampMixin, db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    price = db.Column(Numeric(10, 2), nullable=False)
    purchase_price = db.Column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    stock = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": float(self.price),
            "purchase_price": float(self.purchase_price),
            "stock": self.stock,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Invoice(TimestampMixin, db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(64), unique=True, nullable=False, index=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(32), nullable=True)
    payment_mode = db.Column(db.String(50), nullable=True)
    subtotal = db.Column(Numeric(12, 2), nullable=False)
    discount_percent = db.Column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    discount_amount = db.Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    gst_percent = db.Column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    gst_amount = db.Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    total_amount = db.Column(Numeric(12, 2), nullable=False)
    total_profit = db.Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))

    items = db.relationship(
        "InvoiceItem",
        backref="invoice",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="InvoiceItem.id",
    )


class InvoiceItem(TimestampMixin, db.Model):
    __tablename__ = "invoice_items"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(
        db.Integer, db.ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False
    )
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    product_name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(Numeric(10, 2), nullable=False)
    purchase_price = db.Column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    total = db.Column(Numeric(12, 2), nullable=False)
    profit = db.Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))


__all__ = ["db", "Product", "Invoice", "InvoiceItem"]
