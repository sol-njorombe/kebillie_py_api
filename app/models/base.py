from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import date, datetime

# --- Link Tables ---

class BillSponsorLink(SQLModel, table=True):
    __tablename__ = "bill_sponsors"
    bill_id: Optional[int] = Field(default=None, foreign_key="bills.id", primary_key=True)
    sponsor_id: Optional[int] = Field(default=None, foreign_key="sponsors.id", primary_key=True)

class BillTopicLink(SQLModel, table=True):
    __tablename__ = "bill_topics"
    bill_id: Optional[int] = Field(default=None, foreign_key="bills.id", primary_key=True)
    topic_id: Optional[int] = Field(default=None, foreign_key="topics.id", primary_key=True)

# --- Base Models ---

class BillOrigin(SQLModel, table=True):
    __tablename__ = "bill_origins"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, unique=True, index=True)

    # Relationships
    bills: List["Bill"] = Relationship(back_populates="origin")

class Sponsor(SQLModel, table=True):
    __tablename__ = "sponsors"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, unique=True, index=True)

    # Relationships
    bills: List["Bill"] = Relationship(back_populates="sponsors", link_model=BillSponsorLink)

class Topic(SQLModel, table=True):
    __tablename__ = "topics"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, unique=True, index=True)

    # Relationships
    bills: List["Bill"] = Relationship(back_populates="topics", link_model=BillTopicLink)

class Highlight(SQLModel, table=True):
    __tablename__ = "highlights"
    id: Optional[int] = Field(default=None, primary_key=True)
    bill_id: Optional[int] = Field(default=None, foreign_key="bills.id")
    title: Optional[str] = None
    description: Optional[str] = None

    # Relationships
    bill: Optional["Bill"] = Relationship(back_populates="highlights")

class Bill(SQLModel, table=True):
    __tablename__ = "bills"
    id: Optional[int] = Field(default=None, primary_key=True)
    bill_number: Optional[str] = Field(default=None, max_length=255)
    date_published: Optional[date] = None
    gazette_number: Optional[str] = Field(default=None, max_length=255)
    origin_id: Optional[int] = Field(default=None, foreign_key="bill_origins.id")
    title: Optional[str] = None
    summary: Optional[str] = None
    hook: Optional[str] = None
    details: Optional[str] = None
    source_pdf: Optional[str] = Field(default=None, max_length=255, unique=True)
    source_md: Optional[str] = Field(default=None, max_length=255)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    # Relationships
    origin: Optional[BillOrigin] = Relationship(back_populates="bills")
    highlights: List[Highlight] = Relationship(back_populates="bill")
    sponsors: List[Sponsor] = Relationship(back_populates="bills", link_model=BillSponsorLink)
    topics: List[Topic] = Relationship(back_populates="bills", link_model=BillTopicLink)
