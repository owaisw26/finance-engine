from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ingestion import ManualIngestionRequest, ManualIngestionResponse
from app.services.ingestion import create_manual_ingestion

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
