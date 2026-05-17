from datetime import datetime, timedelta

from sqlalchemy import select

from ..extensions import db
from ..models import Invoice


REPORT_PERIODS = {
    "monthly": 30,
    "3months": 90,
    "6months": 180,
    "yearly": 365,
}


def get_report_payload(period):
    days = REPORT_PERIODS.get(period, 30)
    start_date = datetime.utcnow() - timedelta(days=days)
    invoices = db.session.execute(
        select(Invoice).where(Invoice.date >= start_date).order_by(Invoice.date.desc())
    ).scalars().all()

    total_sales = sum(float(invoice.total_amount) for invoice in invoices)
    total_profit = sum(float(invoice.total_profit) for invoice in invoices)

    return {
        "period": period if period in REPORT_PERIODS else "monthly",
        "invoices": invoices,
        "total_sales": total_sales,
        "total_profit": total_profit,
        "total_invoices": len(invoices),
    }
