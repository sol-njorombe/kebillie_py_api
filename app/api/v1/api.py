from fastapi import APIRouter
from app.api.v1.endpoints import bills, bill_tracker

api_router = APIRouter()
api_router.include_router(bills.router, prefix="/bills", tags=["bills"])
api_router.include_router(bill_tracker.router, prefix="/bill-tracker", tags=["bill-tracker"])
