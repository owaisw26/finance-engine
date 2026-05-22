from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.db.base import Base
from app.models import (
    Embedding,
    Entity,
    FinancialEvent,
    JobRun,
    NarrativeCluster,
    RawDocument,
)


def test_metadata_contains_core_tables() -> None:
    assert set(Base.metadata.tables) == {
        "embeddings",
        "entities",
        "event_entities",
        "financial_events",
        "job_runs",
        "narrative_clusters",
        "narrative_events",
        "raw_documents",
    }


def test_core_model_relationships_can_be_persisted() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        raw_document = RawDocument(
            source_name="seed",
            title="NVIDIA expands AI infrastructure investment",
            body="NVIDIA announced new AI infrastructure partnerships.",
            content_hash="hash-1",
        )
        event = FinancialEvent(
            raw_document=raw_document,
            title="AI infrastructure investment expands",
            summary="NVIDIA announced new infrastructure partnerships.",
            topic="ai infrastructure",
            sentiment="positive",
            importance=4,
        )
        entity = Entity(name="NVIDIA", entity_type="company", symbol="NVDA")
        embedding = Embedding(
            event=event,
            provider="fallback",
            model="fallback",
            vector=[0.1, 0.2, 0.3],
        )
        narrative = NarrativeCluster(
            label="AI infrastructure momentum",
            summary="AI infrastructure investment is strengthening.",
            strength=0.82,
            sentiment="positive",
            trend_direction="strengthening",
        )
        job_run = JobRun(
            job_type="enrichment",
            status="succeeded",
            target_id=raw_document.id,
            attempts=1,
        )

        event.entities.append(entity)
        narrative.events.append(event)
        session.add_all([raw_document, event, entity, embedding, narrative, job_run])
        session.commit()

        saved_event = session.query(FinancialEvent).one()

        assert saved_event.raw_document.source_name == "seed"
        assert saved_event.entities[0].symbol == "NVDA"
        assert saved_event.embeddings[0].vector == [0.1, 0.2, 0.3]
        assert saved_event.narratives[0].label == "AI infrastructure momentum"
        assert session.query(JobRun).one().status == "succeeded"
