from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from app.db.database import get_db
from app.schemas.ocr import OCRScanResponse, OCRReceiptCreateResponse
from app.services.ocr_service import OCRService
from app.api.deps import get_current_user, require_manager

router = APIRouter(prefix="/ocr", tags=["Document OCR & Auto-Fill"])


@router.post("/scan", response_model=OCRScanResponse)
async def scan_document(
    file: UploadFile = File(...),
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Scan a supplier invoice / packing slip document (image, text, or PDF).
    Extracts supplier name, line items, SKUs, and quantities for confirmation.
    """
    try:
        contents = await file.read()
        return OCRService.process_scan(contents, file.filename or "document.txt", conn)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/receipt", response_model=OCRReceiptCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_receipt_from_ocr(
    file: UploadFile = File(...),
    warehouse_id: Optional[str] = Form(None),
    conn=Depends(get_db),
    current_user: dict = Depends(require_manager),
):
    """
    Scan an invoice/packing slip and auto-create a Draft Receipt in StockSense.
    Warehouse staff / manager can review pre-filled lines before final validation.
    """
    try:
        contents = await file.read()
        return OCRService.create_receipt_from_ocr(
            contents, file.filename or "packing_slip.txt", warehouse_id, conn
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
