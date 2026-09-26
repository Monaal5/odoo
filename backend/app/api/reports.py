import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, Response

from app.db.database import get_db
from app.services.report_service import ReportService
from app.api.deps import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports & Exports"])


@router.get(
    "/stock/csv",
    responses={
        200: {
            "content": {"text/csv": {}},
            "description": "Returns inventory stock report in CSV format.",
        }
    },
)
def export_stock_csv(
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Export current stock on-hand as a downloadable CSV file.
    Columns: SKU, Product, Warehouse, Qty.
    """
    csv_data = ReportService.generate_stock_csv(conn)
    buffer = io.BytesIO(csv_data.encode("utf-8"))

    headers = {
        "Content-Disposition": 'attachment; filename="stocksense_inventory_report.csv"'
    }
    return StreamingResponse(buffer, media_type="text/csv", headers=headers)


@router.get(
    "/stock/pdf",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Returns inventory stock audit report in PDF format.",
        }
    },
)
def export_stock_pdf(
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Generate and download a professional PDF stock audit report using ReportLab.
    Includes Company branding, Summary KPIs, Low Stock table, and Signature footer.
    """
    pdf_bytes = ReportService.generate_stock_pdf(conn)

    headers = {
        "Content-Disposition": 'attachment; filename="stocksense_inventory_report.pdf"'
    }
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers=headers,
    )
