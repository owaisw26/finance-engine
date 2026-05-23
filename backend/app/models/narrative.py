from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Index, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.event import FinancialEvent

narrative_events = Table(
    "narrative_events",
    Base.metadata,
    Column("narrative_id", ForeignKey("narrative_clusters.id"), primary_key=True),
    Column("event_id", ForeignKey("financial_events.id"), primary_key=True),
)


class NarrativeCluster(Base):
    __tablename__ = "narrative_clusters"
    __table_args__ = (
        Index("ix_narrative_clusters_strength_trend", "strength", "trend_direction"),
    )

    label: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    strength: Mapped[float] = mapped_column(default=0.0, nullable=False)
    sentiment: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    trend_direction: Mapped[str | None] = mapped_column(String(40), nullable=True)

    events: Mapped[list["FinancialEvent"]] = relationship(
        secondary=narrative_events,
        back_populates="narratives",
    )
