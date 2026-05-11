from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session

from app.crud import crud_bill
from app.schemas.bill import BillRead, BillCreate, BillEmbedRequest, BillSearchResult
from app.db.session import get_db
from app.tasks.embedding_tasks import process_bill_embeddings
from app.services.embedding import get_embedding_service
from app.core.config import settings

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

@router.get("/search", response_model=List[BillSearchResult])
def search_bills(
    query: str,
    limit: int = 5,
    db: Session = Depends(get_db)
) -> Any:
    """
    Search bills using semantic vector similarity.
    """
    # 1. Vectorize the string query
    service = get_embedding_service()
    search_vector = service.get_search_vector(query)
    
    # 2. Query the database using pgvector
    results = crud_bill.search_bills_by_similarity(
        db=db, 
        query_vector=search_vector, 
        limit=limit
    )
    
    # 3. Format response
    return [{"bill": bill, "similarity_score": score} for bill, score in results]

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

@router.post("/embed", status_code=202)
def trigger_embedding(
    request: BillEmbedRequest,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Trigger a background task to process embeddings for specified bills.
    """
    if not request.bill_ids and not request.all_bills:
        raise HTTPException(status_code=400, detail="Must provide either bill_ids or set all_bills=True")
        
    background_tasks.add_task(
        process_bill_embeddings, 
        bill_ids=request.bill_ids, 
        all_bills=request.all_bills
    )
    
    return {"message": "Embedding task started in the background."}
