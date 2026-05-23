from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.event import FinancialEvent


class RawDocument(Base):
    __tablename__ = "raw_documents"
    __table_args__ = (
        UniqueConstraint("content_hash", name="uq_raw_documents_content_hash"),
    )

    source_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(nullable=True, index=True)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    ingestion_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    events: Mapped[list["FinancialEvent"]] = relationship(back_populates="raw_document")
