from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import FinancialEvent, JobRun, RawDocument
from app.services.ingestion import generate_content_hash


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        yield session

    Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_manual_ingestion_creates_document_event_and_job(
    client: TestClient,
    db_session: Session,
) -> None:
    payload = {
        "source_name": "manual",
        "title": "NVIDIA reports stronger data center demand",
        "body": "NVIDIA reported stronger-than-expected data center revenue as cloud providers continued spending on AI infrastructure.",
        "source_url": "https://example.com/nvidia",
        "ingestion_metadata": {"category": "earnings"},
    }

    response = client.post("/ingest/manual", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "created"
    assert data["title"] == payload["title"]
    assert data["summary"].startswith("NVIDIA reported")

    raw_document = db_session.query(RawDocument).one()
    event = db_session.query(FinancialEvent).one()
    job_run = db_session.query(JobRun).one()

    assert raw_document.content_hash == generate_content_hash(
        payload["title"],
        payload["body"],
    )
    assert event.raw_document_id == raw_document.id
    assert event.topic is None
    assert event.sentiment is None
    assert job_run.job_type == "manual_ingestion"
    assert job_run.status == "succeeded"
    assert job_run.target_id == raw_document.id
    assert job_run.started_at is not None
    assert job_run.finished_at is not None


def test_manual_ingestion_is_idempotent(
    client: TestClient,
    db_session: Session,
) -> None:
    payload = {
        "source_name": "manual",
        "title": "Oil prices rise after supply disruption concerns",
        "body": "Oil prices rose after supply disruption concerns outweighed softer demand indicators. Energy traders monitored geopolitical risk.",
    }

    first_response = client.post("/ingest/manual", json=payload)
    second_response = client.post("/ingest/manual", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 200
    assert second_response.json()["status"] == "duplicate"
    assert second_response.json()["raw_document_id"] == first_response.json()["raw_document_id"]
    assert (
        second_response.json()["financial_event_id"]
        == first_response.json()["financial_event_id"]
    )
    assert second_response.json()["job_run_id"] is None
    assert db_session.query(RawDocument).count() == 1
    assert db_session.query(FinancialEvent).count() == 1
    assert db_session.query(JobRun).count() == 1
