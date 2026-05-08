from typing import Optional
import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import pgvector.sqlalchemy

class Base(DeclarativeBase):
    pass


class BillOrigins(Base):
    __tablename__ = 'bill_origins'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='bill_origins_pkey'),
        UniqueConstraint('name', name='bill_origins_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    bills: Mapped[list['Bills']] = relationship('Bills', back_populates='origin')


class BillsStaging(Base):
    __tablename__ = 'bills_staging'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='bills_staging_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    imported: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))


class Sponsors(Base):
    __tablename__ = 'sponsors'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='sponsors_pkey'),
        UniqueConstraint('name', name='sponsors_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    bill: Mapped[list['Bills']] = relationship('Bills', secondary='bill_sponsors', back_populates='sponsor')


class Topics(Base):
    __tablename__ = 'topics'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='topics_pkey'),
        UniqueConstraint('name', name='topics_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    bill: Mapped[list['Bills']] = relationship('Bills', secondary='bill_topics', back_populates='topic')


class Bills(Base):
    __tablename__ = 'bills'
    __table_args__ = (
        ForeignKeyConstraint(['origin_id'], ['bill_origins.id'], ondelete='SET NULL', name='bills_origin_id_fkey'),
        PrimaryKeyConstraint('id', name='bills_pkey'),
        UniqueConstraint('source_pdf', name='bills_source_pdf_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bill_number: Mapped[Optional[str]] = mapped_column(String(255))
    date_published: Mapped[Optional[datetime.date]] = mapped_column(Date)
    gazette_number: Mapped[Optional[str]] = mapped_column(String(255))
    origin_id: Mapped[Optional[int]] = mapped_column(Integer)
    title: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    hook: Mapped[Optional[str]] = mapped_column(Text)
    details: Mapped[Optional[str]] = mapped_column(Text)
    source_pdf: Mapped[Optional[str]] = mapped_column(String(255))
    source_md: Mapped[Optional[str]] = mapped_column(String(255))
    embedding_jina: Mapped[Optional[list[float]]] = mapped_column(pgvector.sqlalchemy.Vector(1024))
    embedding_gemma: Mapped[Optional[list[float]]] = mapped_column(pgvector.sqlalchemy.Vector(768))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))

    origin: Mapped[Optional['BillOrigins']] = relationship('BillOrigins', back_populates='bills')
    sponsor: Mapped[list['Sponsors']] = relationship('Sponsors', secondary='bill_sponsors', back_populates='bill')
    topic: Mapped[list['Topics']] = relationship('Topics', secondary='bill_topics', back_populates='bill')
    highlights: Mapped[list['Highlights']] = relationship('Highlights', back_populates='bill')


t_bill_sponsors = Table(
    'bill_sponsors', Base.metadata,
    Column('bill_id', Integer, primary_key=True),
    Column('sponsor_id', Integer, primary_key=True),
    ForeignKeyConstraint(['bill_id'], ['bills.id'], ondelete='CASCADE', name='bill_sponsors_bill_id_fkey'),
    ForeignKeyConstraint(['sponsor_id'], ['sponsors.id'], ondelete='CASCADE', name='bill_sponsors_sponsor_id_fkey'),
    PrimaryKeyConstraint('bill_id', 'sponsor_id', name='bill_sponsors_pkey')
)


t_bill_topics = Table(
    'bill_topics', Base.metadata,
    Column('bill_id', Integer, primary_key=True),
    Column('topic_id', Integer, primary_key=True),
    ForeignKeyConstraint(['bill_id'], ['bills.id'], ondelete='CASCADE', name='bill_topics_bill_id_fkey'),
    ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE', name='bill_topics_topic_id_fkey'),
    PrimaryKeyConstraint('bill_id', 'topic_id', name='bill_topics_pkey')
)


class Highlights(Base):
    __tablename__ = 'highlights'
    __table_args__ = (
        ForeignKeyConstraint(['bill_id'], ['bills.id'], ondelete='CASCADE', name='highlights_bill_id_fkey'),
        PrimaryKeyConstraint('id', name='highlights_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bill_id: Mapped[Optional[int]] = mapped_column(Integer)
    title: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)

    bill: Mapped[Optional['Bills']] = relationship('Bills', back_populates='highlights')
