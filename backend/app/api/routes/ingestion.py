from urllib.error import URLError

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.schemas.ingestion import (
    ManualIngestionRequest,
    ManualIngestionResponse,
    RssIngestionRequest,
    RssIngestionResponse,
)
from app.services.ingestion import create_manual_ingestion, create_rss_ingestion

router = APIRouter(prefix="/ingest", tags=["ingestion"])


@router.post(
    "/manual",
    response_model=ManualIngestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_manual(
    payload: ManualIngestionRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> ManualIngestionResponse:
    result = create_manual_ingestion(db=db, payload=payload)

    if result.status == "duplicate":
        response.status_code = status.HTTP_200_OK

    return ManualIngestionResponse(
        status=result.status,
        raw_document_id=result.raw_document.id,
        financial_event_id=result.financial_event.id,
        job_run_id=result.job_run.id if result.job_run else None,
        content_hash=result.raw_document.content_hash,
        title=result.financial_event.title,
        summary=result.financial_event.summary,
    )


@router.post("/run", response_model=RssIngestionResponse)
def run_rss_ingestion(
    payload: RssIngestionRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> RssIngestionResponse:
    try:
        result = create_rss_ingestion(
            db=db,
            feed_url=payload.feed_url,
            source_name=payload.source_name,
            limit=payload.limit,
            timeout_seconds=settings.rss_request_timeout_seconds,
        )
    except (ValueError, URLError, TimeoutError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"RSS ingestion failed: {exc}",
        ) from exc

    return RssIngestionResponse(
        feed_url=result.feed_url,
        source_name=result.source_name,
        fetched_count=result.fetched_count,
        created_count=result.created_count,
        duplicate_count=result.duplicate_count,
        skipped_count=result.skipped_count,
        items=result.items,
    )
