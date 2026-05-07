from sqlmodel import create_engine, Session
from app.core.config import settings

# create_engine connects to the database
engine = create_engine(settings.DATABASE_URL, echo=False)

def get_db():
    """
    Dependency to provide a database session for each request.
    It yields the session and ensures it's closed after the request is finished.
    """
    with Session(engine) as session:
        yield session
