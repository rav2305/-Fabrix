import io

from flask import Blueprint, Response, current_app, render_template, request, send_from_directory
from openpyxl import Workbook

from ...services.billing_service import get_invoice_or_404
from ...services.dashboard_service import get_dashboard_stats
from ...services.reporting_service import get_report_payload


web_bp = Blueprint("web", __name__)


@web_bp.get("/")
def dashboard():
    return render_template("dashboard.html", stats=get_dashboard_stats())


@web_bp.get("/inventory/manage")
def inventory_page():
    return render_template("inventory.html")


@web_bp.get("/billing")
def billing():
    return render_template("billing.html")


@web_bp.get("/invoice/<int:invoice_id>")
def view_invoice(invoice_id):
    return render_template("invoice.html", invoice=get_invoice_or_404(invoice_id))


@web_bp.get("/reports")
def reports():
    return _render_report(period=request.args.get("period", "monthly"))


@web_bp.get("/reports/<period>")
def reports_by_period(period):
    return _render_report(period=period)


def _render_report(period):
    report = get_report_payload(period=period)
    return render_template(
        "reports.html",
        invoices=report["invoices"],
        period=report["period"],
        total_sales=report["total_sales"],
        total_profit=report["total_profit"],
        total_invoices=report["total_invoices"],
    )


@web_bp.get("/download-demo")
def download_demo():
    output = io.BytesIO()
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Sheet1"
    sheet.append(["Product Name", "Qty", "Selling Price", "Price for us"])
    sheet.append(["Jeans", 200, 1000, 440])
    sheet.append(["Shirts", 300, 600, 380])
    workbook.save(output)
    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={"Content-Disposition": "attachment; filename=demo_inventory.xlsx"},
    )


@web_bp.get("/manifest.webmanifest")
def web_manifest():
    return send_from_directory(
        current_app.static_folder,
        "pwa/manifest.webmanifest",
        mimetype="application/manifest+json",
    )


@web_bp.get("/service-worker.js")
def service_worker():
    response = send_from_directory(
        current_app.static_folder,
        "js/service-worker.js",
        mimetype="application/javascript",
    )
    response.headers["Cache-Control"] = "no-cache"
    return response
