from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import date, datetime
from sqlalchemy import Column
import pgvector.sqlalchemy

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
    embedding_jina: Optional[List[float]] = Field(
        default=None, 
        sa_column=Column(pgvector.sqlalchemy.Vector(1024))
    )
    embedding_gemma: Optional[List[float]] = Field(
        default=None, 
        sa_column=Column(pgvector.sqlalchemy.Vector(768))
    )
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    # Relationships
    origin: Optional[BillOrigin] = Relationship(back_populates="bills")
    highlights: List[Highlight] = Relationship(back_populates="bill")
    sponsors: List[Sponsor] = Relationship(back_populates="bills", link_model=BillSponsorLink)
    topics: List[Topic] = Relationship(back_populates="bills", link_model=BillTopicLink)

    def get_embeddable_text(self) -> str:
        """Constructs a combined string of bill content for embedding."""
        parts = []
        if self.bill_number:
            parts.append(f"Bill Number: {self.bill_number}")
        if self.date_published:
            parts.append(f"Date Published: {self.date_published}")
        if self.gazette_number:
            parts.append(f"Gazette Number: {self.gazette_number}")
        if self.origin and self.origin.name:
            parts.append(f"Origin: {self.origin.name}")
        if self.sponsors:
            sponsor_names = ", ".join([s.name for s in self.sponsors if s.name])
            if sponsor_names:
                parts.append(f"Sponsors: {sponsor_names}")
        if self.topics:
            topic_names = ", ".join([t.name for t in self.topics if t.name])
            if topic_names:
                parts.append(f"Topics: {topic_names}")
        if self.title:
            parts.append(f"Title: {self.title}")
        if self.hook:
            parts.append(f"Hook: {self.hook}")
        if self.details:
            parts.append(f"Details: {self.details}")
            
        return "\n".join(parts)
