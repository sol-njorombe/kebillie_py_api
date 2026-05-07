from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.crud import crud_bill
from app.schemas.bill import BillRead, BillCreate
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[BillRead])
def read_bills(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve bills.
    """
    bills = crud_bill.get_bills(db, skip=skip, limit=limit)
    return bills

@router.post("/", response_model=BillRead)
def create_bill(
    *,
    db: Session = Depends(get_db),
    bill_in: BillCreate,
) -> Any:
    """
    Create new bill.
    """
    bill = crud_bill.create_bill(db, bill_in=bill_in)
    return bill

@router.get("/{bill_id}", response_model=BillRead)
def read_bill(
    *,
    db: Session = Depends(get_db),
    bill_id: int,
) -> Any:
    """
    Get bill by ID.
    """
    bill = crud_bill.get_bill(db, bill_id=bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill
