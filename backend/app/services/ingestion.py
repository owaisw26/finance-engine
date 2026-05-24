from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import re
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import utc_now
from app.models import FinancialEvent, JobRun, RawDocument
from app.schemas.ingestion import ManualIngestionRequest, RssIngestedItem
from app.services.rss_connector import fetch_rss_xml, parse_rss_xml


@dataclass(frozen=True)
class ManualIngestionResult:
    status: Literal["created", "duplicate"]
    raw_document: RawDocument
    financial_event: FinancialEvent
    job_run: JobRun | None


@dataclass(frozen=True)
class RssIngestionResult:
    feed_url: str
    source_name: str
    fetched_count: int
    created_count: int
    duplicate_count: int
    skipped_count: int
    items: list[RssIngestedItem]


@dataclass(frozen=True)
class IngestionDocument:
    source_name: str
    title: str
    body: str
    source_url: str | None = None
    published_at: datetime | None = None
    ingestion_metadata: dict[str, Any] | None = None


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
    document = IngestionDocument(
        source_name=payload.source_name,
        source_url=payload.source_url,
        title=payload.title,
        body=payload.body,
        published_at=payload.published_at,
        ingestion_metadata=payload.ingestion_metadata,
    )
    return _ingest_document(
        db=db,
        document=document,
        job_type="manual_ingestion",
    )


def create_rss_ingestion(
    db: Session,
    feed_url: str,
    source_name: str | None,
    limit: int,
    timeout_seconds: int,
) -> RssIngestionResult:
    xml_text = fetch_rss_xml(feed_url=feed_url, timeout_seconds=timeout_seconds)
    feed = parse_rss_xml(xml_text, fallback_source_name=source_name or "rss")
    resolved_source_name = source_name or feed.source_name

    items: list[RssIngestedItem] = []
    created_count = 0
    duplicate_count = 0
    skipped_count = 0

    for rss_item in feed.items[:limit]:
        if not rss_item.body:
            skipped_count += 1
            items.append(
                RssIngestedItem(
                    status="skipped",
                    title=rss_item.title,
                    source_url=rss_item.source_url,
                    reason="RSS item did not include body text",
                ),
            )
            continue

        result = _ingest_document(
            db=db,
            document=IngestionDocument(
                source_name=resolved_source_name,
                source_url=rss_item.source_url,
                title=rss_item.title,
                body=rss_item.body,
                published_at=rss_item.published_at,
                ingestion_metadata={
                    "connector": "rss",
                    "feed_url": feed_url,
                },
            ),
            job_type="rss_ingestion",
        )

        if result.status == "created":
            created_count += 1
        else:
            duplicate_count += 1

        items.append(
            RssIngestedItem(
                status=result.status,
                title=result.financial_event.title,
                raw_document_id=result.raw_document.id,
                financial_event_id=result.financial_event.id,
                source_url=result.raw_document.source_url,
            ),
        )

    return RssIngestionResult(
        feed_url=feed_url,
        source_name=resolved_source_name,
        fetched_count=len(feed.items),
        created_count=created_count,
        duplicate_count=duplicate_count,
        skipped_count=skipped_count,
        items=items,
    )


def _ingest_document(
    db: Session,
    document: IngestionDocument,
    job_type: str,
) -> ManualIngestionResult:
    content_hash = generate_content_hash(document.title, document.body)

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
                raw_document=existing_document,
                published_at=existing_document.published_at,
            )
            db.add(existing_event)
            db.commit()
            db.refresh(existing_event)

        return ManualIngestionResult(
            status="duplicate",
            raw_document=existing_document,
            financial_event=existing_event,
            job_run=None,
        )

    raw_document = RawDocument(
        source_name=normalize_text(document.source_name),
        source_url=document.source_url,
        title=normalize_text(document.title),
        body=normalize_text(document.body),
        published_at=document.published_at,
        content_hash=content_hash,
        ingestion_metadata=document.ingestion_metadata,
    )

    financial_event = _create_initial_event(
        raw_document=raw_document,
        published_at=document.published_at,
    )
    db.add_all([raw_document, financial_event])
    db.flush()

    job_finished_at = utc_now()
    job_run = JobRun(
        job_type=job_type,
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
    raw_document: RawDocument,
    published_at: datetime | None,
) -> FinancialEvent:
    return FinancialEvent(
        raw_document=raw_document,
        title=raw_document.title,
        summary=build_initial_summary(raw_document.body),
        topic=None,
        sentiment=None,
        importance=0,
        occurred_at=published_at,
    )
