"""
Bill Tracker PDF extraction endpoint.

POST /api/v1/bill-tracker/extract
Accepts a PDF file upload and returns structured JSON of extracted bills.
"""
import logging
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.bill_tracker import BillTrackerExtractionResponse
from app.services.bill_tracker import get_bill_tracker_extractor

logger = logging.getLogger(__name__)

router = APIRouter()

# 20 MB max – the Bills Tracker PDFs are typically under 5 MB
MAX_FILE_SIZE = 20 * 1024 * 1024


@router.post("/extract", response_model=BillTrackerExtractionResponse)
async def extract_bill_tracker(
    file: UploadFile = File(..., description="National Assembly Bills Tracker PDF"),
) -> Any:
    """
    Upload a Kenya National Assembly Bills Tracker PDF and receive
    structured JSON with one record per bill.
    """
    # ── Validate content type ────────────────────────────────────────
    if file.content_type not in ("application/pdf", "application/x-pdf"):
        raise HTTPException(
            status_code=400,
            detail=f"Expected a PDF file, got content-type: {file.content_type}",
        )

    # ── Read and validate size ───────────────────────────────────────
    pdf_bytes = await file.read()

    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(pdf_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(pdf_bytes)} bytes). Maximum is {MAX_FILE_SIZE} bytes.",
        )

    # ── Validate PDF magic bytes ─────────────────────────────────────
    if not pdf_bytes[:5] == b"%PDF-":
        raise HTTPException(
            status_code=400,
            detail="File does not appear to be a valid PDF.",
        )

    # ── Extract ──────────────────────────────────────────────────────
    try:
        extractor = get_bill_tracker_extractor()
        result = extractor.extract(pdf_bytes)
    except Exception as exc:
        logger.error("PDF extraction failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"PDF extraction failed: {exc}",
        )

    return result
