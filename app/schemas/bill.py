from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

# --- Origin Schemas ---
class OriginBase(BaseModel):
    name: str

class OriginRead(OriginBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Sponsor Schemas ---
class SponsorBase(BaseModel):
    name: str

class SponsorRead(SponsorBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Topic Schemas ---
class TopicBase(BaseModel):
    name: str

class TopicRead(TopicBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Highlight Schemas ---
class HighlightBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class HighlightRead(HighlightBase):
    id: int
    bill_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

# --- Bill Schemas ---
class BillBase(BaseModel):
    bill_number: Optional[str] = None
    date_published: Optional[date] = None
    gazette_number: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    hook: Optional[str] = None
    details: Optional[str] = None
    source_pdf: Optional[str] = None
    source_md: Optional[str] = None

class BillRead(BillBase):
    id: int
    origin_id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    # Relationships
    origin: Optional[OriginRead] = None
    sponsors: List[SponsorRead] = []
    topics: List[TopicRead] = []
    highlights: List[HighlightRead] = []

    model_config = ConfigDict(from_attributes=True)

class BillCreate(BillBase):
    origin_id: Optional[int] = None
    # For a full create, you might accept lists of IDs
    sponsor_ids: Optional[List[int]] = []
    topic_ids: Optional[List[int]] = []

class BillUpdate(BillBase):
    # All fields optional for update
    pass

class BillEmbedRequest(BaseModel):
    bill_ids: Optional[List[int]] = None
    all_bills: bool = False

class BillSearchResult(BaseModel):
    bill: BillRead
    similarity_score: float
