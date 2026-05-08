import logging
from typing import Optional, List
from sqlmodel import Session, select
from app.db.session import engine
from app.models.base import Bill
from app.services.embedding import get_embedding_service
from app.core.config import settings

logger = logging.getLogger(__name__)

def process_bill_embeddings(bill_ids: Optional[List[int]] = None, all_bills: bool = False):
    """
    Background task to fetch bills and update their embedding vectors.
    Since this runs in the background, we must open our own database session.
    """
    if not bill_ids and not all_bills:
        logger.warning("No bill IDs provided and all_bills is False. Nothing to process.")
        return

    logger.info("Initializing Embedding Service...")
    service = get_embedding_service()
    
    # Track metrics
    success_count = 0
    failure_count = 0

    with Session(engine) as session:
        # Build query
        statement = select(Bill)
        if not all_bills and bill_ids:
            statement = statement.where(Bill.id.in_(bill_ids))
            
        bills = session.exec(statement).all()
        
        logger.info(f"Found {len(bills)} bills to process for embeddings.")
        
        for bill in bills:
            try:
                # 1. Get the formatted text
                embed_text = bill.get_embeddable_text()
                if not embed_text:
                    logger.warning(f"Bill ID {bill.id} has no embeddable text. Skipping.")
                    continue
                
                # 2. Vectorize using the service
                vector = service.get_content_vector(embed_text)
                
                # 3. Update the appropriate field
                if settings.ACTIVE_EMBEDDING_MODEL.lower() == "jina":
                    bill.embedding_jina = vector
                elif settings.ACTIVE_EMBEDDING_MODEL.lower() == "gemma":
                    bill.embedding_gemma = vector
                
                # Commit the change for this specific bill
                session.add(bill)
                session.commit()
                
                success_count += 1
                logger.info(f"Successfully updated embeddings for Bill ID {bill.id}.")
                
            except Exception as e:
                # Log the error to the terminal, but continue processing the next bill
                logger.error(f"Failed to process embeddings for Bill ID {bill.id}. Error: {str(e)}")
                failure_count += 1
                session.rollback() # Important: rollback the failed transaction to keep the session healthy
                
    logger.info(f"Embedding Task Complete. Success: {success_count}, Failures: {failure_count}")
