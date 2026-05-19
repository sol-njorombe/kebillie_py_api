from typing import Optional, List
from pydantic import BaseModel


class BillTrackerRow(BaseModel):
    """Represents a single bill extracted from the National Assembly Bills Tracker PDF."""
    serial_number: Optional[str] = None
    bill: Optional[str] = None
    sponsor: Optional[str] = None
    na_sen_bill_no: Optional[str] = None
    dated: Optional[str] = None
    maturity_date: Optional[str] = None
    gazette_no: Optional[str] = None
    first_read: Optional[str] = None
    second_read: Optional[str] = None
    third_read: Optional[str] = None
    remarks: Optional[str] = None
    assent: Optional[str] = None


class BillTrackerExtractionResponse(BaseModel):
    """Response schema for the bill tracker PDF extraction endpoint."""
    page_count: int
    bill_count: int
    bills: List[BillTrackerRow]
