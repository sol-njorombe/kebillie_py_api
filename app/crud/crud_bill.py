from typing import List, Optional
from sqlmodel import Session, select
from app.models.base import Bill, Sponsor, Topic, BillSponsorLink, BillTopicLink
from app.schemas.bill import BillCreate

def get_bill(db: Session, bill_id: int) -> Optional[Bill]:
    return db.get(Bill, bill_id)

def get_bills(db: Session, skip: int = 0, limit: int = 100) -> List[Bill]:
    statement = select(Bill).offset(skip).limit(limit)
    results = db.exec(statement).all()
    return results

def create_bill(db: Session, bill_in: BillCreate) -> Bill:
    db_bill = Bill(
        bill_number=bill_in.bill_number,
        date_published=bill_in.date_published,
        gazette_number=bill_in.gazette_number,
        title=bill_in.title,
        summary=bill_in.summary,
        hook=bill_in.hook,
        details=bill_in.details,
        source_pdf=bill_in.source_pdf,
        source_md=bill_in.source_md,
        origin_id=bill_in.origin_id
    )
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    
    # Handle sponsors
    if bill_in.sponsor_ids:
        for sponsor_id in bill_in.sponsor_ids:
            # Check if sponsor exists
            if db.get(Sponsor, sponsor_id):
                link = BillSponsorLink(bill_id=db_bill.id, sponsor_id=sponsor_id)
                db.add(link)
    
    # Handle topics
    if bill_in.topic_ids:
        for topic_id in bill_in.topic_ids:
            if db.get(Topic, topic_id):
                link = BillTopicLink(bill_id=db_bill.id, topic_id=topic_id)
                db.add(link)
                
    db.commit()
    db.refresh(db_bill)
    return db_bill

def search_bills_by_similarity(db: Session, query_vector: list[float], limit: int = 5, min_similarity: float = 0.5):
    from app.core.config import settings
    
    if settings.ACTIVE_EMBEDDING_MODEL.lower() == "jina":
        cosine_distance = Bill.embedding_jina.cosine_distance(query_vector)
    else:
        cosine_distance = Bill.embedding_gemma.cosine_distance(query_vector)
        
    similarity = (1 - cosine_distance).label("similarity_score")
    
    # Use the math expression directly in the where clause to avoid alias issues
    statement = (
        select(Bill, similarity)
        .where((1 - cosine_distance) >= min_similarity)
        .order_by(cosine_distance)
        .limit(limit)
    )
    
    return db.exec(statement).all()
