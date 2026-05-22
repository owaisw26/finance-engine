from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Embedding(Base):
    __tablename__ = "embeddings"

    event_id: Mapped[str] = mapped_column(
        ForeignKey("financial_events.id"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(80), nullable=False, default="fallback")
    model: Mapped[str] = mapped_column(String(120), nullable=False, default="fallback")
    vector: Mapped[list[float]] = mapped_column(JSON, nullable=False)

    event: Mapped["FinancialEvent"] = relationship(back_populates="embeddings")
