from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ManualIngestionRequest(BaseModel):
    source_name: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=500)
    body: str = Field(min_length=20)
    source_url: str | None = Field(default=None, max_length=1000)
    published_at: datetime | None = None
    ingestion_metadata: dict[str, Any] | None = None


class ManualIngestionResponse(BaseModel):
    status: Literal["created", "duplicate"]
    raw_document_id: str
    financial_event_id: str
    job_run_id: str | None
    content_hash: str
    title: str
    summary: str | None


class RssIngestionRequest(BaseModel):
    feed_url: str = Field(min_length=1, max_length=1000)
    source_name: str | None = Field(default=None, max_length=120)
    limit: int = Field(default=10, ge=1, le=50)


class RssIngestedItem(BaseModel):
    status: Literal["created", "duplicate", "skipped"]
    title: str
    raw_document_id: str | None = None
    financial_event_id: str | None = None
    source_url: str | None = None
    reason: str | None = None


class RssIngestionResponse(BaseModel):
    feed_url: str
    source_name: str
    fetched_count: int
    created_count: int
    duplicate_count: int
    skipped_count: int
    items: list[RssIngestedItem]
