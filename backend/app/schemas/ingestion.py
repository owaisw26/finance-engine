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
