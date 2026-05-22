from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, Table, Text, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

event_entities = Table(
    "event_entities",
    Base.metadata,
    Column("event_id", ForeignKey("financial_events.id"), primary_key=True),
    Column("entity_id", ForeignKey("entities.id"), primary_key=True),
)


class FinancialEvent(Base):
    __tablename__ = "financial_events"
    __table_args__ = (
        Index("ix_financial_events_topic_sentiment", "topic", "sentiment"),
    )

    raw_document_id: Mapped[str] = mapped_column(
        ForeignKey("raw_documents.id"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    topic: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    sentiment: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    importance: Mapped[int] = mapped_column(default=0, nullable=False)
    occurred_at: Mapped[datetime | None] = mapped_column(nullable=True, index=True)

    raw_document: Mapped["RawDocument"] = relationship(back_populates="events")
    entities: Mapped[list["Entity"]] = relationship(
        secondary=event_entities,
        back_populates="events",
    )
    embeddings: Mapped[list["Embedding"]] = relationship(back_populates="event")
    narratives: Mapped[list["NarrativeCluster"]] = relationship(
        secondary="narrative_events",
        back_populates="events",
    )
