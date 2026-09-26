import logging
from typing import Dict, Any, List, Optional
from app.db.database import dict_cursor
from app.services.report_service import ReportService

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Analytics and Reporting Service.
    Implements Shared Report Architecture bridging DB -> Data Analytics -> CSV/PDF Reports.
    """

    @staticmethod
    def get_inventory_analytics(conn) -> Dict[str, Any]:
        """Compute aggregated inventory statistics, low stock counts, and total valuation metrics."""
        stock_data = ReportService.get_stock_data(conn)
        total_skus = len(set(r["SKU"] for r in stock_data)) if stock_data else 0
        total_units = sum(r["Qty"] for r in stock_data) if stock_data else 0.0
        low_stock_items = [r for r in stock_data if r["IsLowStock"]]

        with dict_cursor(conn) as cur:
            cur.execute("SELECT COUNT(*) AS total FROM receipts WHERE status = 'Draft'")
            pending_receipts = cur.fetchone()["total"]

            cur.execute("SELECT COUNT(*) AS total FROM deliveries WHERE status = 'Draft'")
            pending_deliveries = cur.fetchone()["total"]

            cur.execute("SELECT COUNT(*) AS total FROM audit_logs")
            total_audit_events = cur.fetchone()["total"]

        return {
            "total_skus": total_skus,
            "total_units": total_units,
            "low_stock_count": len(low_stock_items),
            "pending_receipts": pending_receipts,
            "pending_deliveries": pending_deliveries,
            "total_audit_events": total_audit_events,
            "stock_items": stock_data,
        }

    @staticmethod
    def export_csv_report(conn) -> str:
        """Generate CSV export via ReportService."""
        return ReportService.generate_stock_csv(conn)

    @staticmethod
    def export_pdf_report(conn) -> bytes:
        """Generate PDF export via ReportService."""
        return ReportService.generate_stock_pdf(conn)
