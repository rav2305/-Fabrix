from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select

from ..extensions import db
from ..models import Invoice, Product


def get_dashboard_stats():
    total_products = db.session.execute(
        select(func.count(Product.id))
    ).scalar_one()
    total_stock = db.session.execute(
        select(func.coalesce(func.sum(Product.stock), 0))
    ).scalar_one()

    today = date.today()
    start_of_day = datetime.combine(today, time.min)
    end_of_day = start_of_day + timedelta(days=1)

    sales_totals = db.session.execute(
        select(
            func.coalesce(func.sum(Invoice.total_amount), 0),
            func.coalesce(func.sum(Invoice.total_profit), 0),
        ).where(Invoice.date >= start_of_day, Invoice.date < end_of_day)
    ).one()

    return {
        "total_products": int(total_products or 0),
        "total_stock": int(total_stock or 0),
        "today_sales": float(sales_totals[0] or 0),
        "today_profit": float(sales_totals[1] or 0),
        "as_of": datetime.utcnow().isoformat(),
    }
