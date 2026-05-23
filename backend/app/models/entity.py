from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.event import FinancialEvent


class Entity(Base):
    __tablename__ = "entities"
    __table_args__ = (
        UniqueConstraint("name", "entity_type", name="uq_entities_name_entity_type"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    symbol: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)

    events: Mapped[list["FinancialEvent"]] = relationship(
        secondary="event_entities",
        back_populates="entities",
    )
