from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import re
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import utc_now
from app.models import FinancialEvent, JobRun, RawDocument
from app.schemas.ingestion import ManualIngestionRequest


@dataclass(frozen=True)
class ManualIngestionResult:
    status: Literal["created", "duplicate"]
    raw_document: RawDocument
    financial_event: FinancialEvent
    job_run: JobRun | None


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def generate_content_hash(title: str, body: str) -> str:
    normalized = f"{normalize_text(title)}\n{normalize_text(body)}".lower()
    return sha256(normalized.encode("utf-8")).hexdigest()

def build_initial_summary(body: str, max_length: int = 320) -> str:
    normalized = normalize_text(body)
    first_sentence = re.split(r"(?<=[.!?])\s+", normalized, maxsplit=1)[0]

    if len(first_sentence) <= max_length:
        return first_sentence

    return f"{first_sentence[: max_length - 3].rstrip()}..."

def create_manual_ingestion(
    db: Session,
    payload: ManualIngestionRequest,
) -> ManualIngestionResult:
    content_hash = generate_content_hash(payload.title, payload.body)

    existing_document = db.scalar(
        select(RawDocument).where(RawDocument.content_hash == content_hash),
    )

    if existing_document is not None:
        existing_event = db.scalar(
            select(FinancialEvent).where(
                FinancialEvent.raw_document_id == existing_document.id,
            ),
        )

        if existing_event is None:
            existing_event = _create_initial_event(
                db=db,
                raw_document=existing_document,
                published_at=existing_document.published_at,
            )
            db.commit()
            db.refresh(existing_event)

        return ManualIngestionResult(
            status="duplicate",
            raw_document=existing_document,
            financial_event=existing_event,
            job_run=None,
        )

    raw_document = RawDocument(
        source_name=normalize_text(payload.source_name),
        source_url=payload.source_url,
        title=normalize_text(payload.title),
        body=normalize_text(payload.body),
        published_at=payload.published_at,
        content_hash=content_hash,
        ingestion_metadata=payload.ingestion_metadata,
    )

    financial_event = _create_initial_event(
        db=db,
        raw_document=raw_document,
        published_at=payload.published_at,
    )
    db.add_all([raw_document, financial_event])
    db.flush()

    job_finished_at = utc_now()
    job_run = JobRun(
        job_type="manual_ingestion",
        status="succeeded",
        target_id=raw_document.id,
        attempts=1,
        started_at=job_finished_at,
        finished_at=job_finished_at,
        job_metadata={"source_name": raw_document.source_name},
    )

    db.add(job_run)
    db.commit()
    db.refresh(raw_document)
    db.refresh(financial_event)
    db.refresh(job_run)

    return ManualIngestionResult(
        status="created",
        raw_document=raw_document,
        financial_event=financial_event,
        job_run=job_run,
    )


def _create_initial_event(
    db: Session,
    raw_document: RawDocument,
    published_at: datetime | None,
) -> FinancialEvent:
    financial_event = FinancialEvent(
        raw_document=raw_document,
        title=raw_document.title,
        summary=build_initial_summary(raw_document.body),
        topic=None,
        sentiment=None,
        importance=0,
        occurred_at=published_at,
    )
    db.add(financial_event)
    return financial_event
