"""initial intelligence schema

Revision ID: 0001_initial_intelligence_schema
Revises:
Create Date: 2026-05-22
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_intelligence_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "entities",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_entities")),
        sa.UniqueConstraint("name", "entity_type", name="uq_entities_name_entity_type"),
    )
    op.create_index(op.f("ix_entities_entity_type"), "entities", ["entity_type"], unique=False)
    op.create_index(op.f("ix_entities_name"), "entities", ["name"], unique=False)
    op.create_index(op.f("ix_entities_symbol"), "entities", ["symbol"], unique=False)

    op.create_table(
        "job_runs",
        sa.Column("job_type", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("target_id", sa.String(length=64), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("job_metadata", sa.JSON(), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_job_runs")),
    )
    op.create_index(op.f("ix_job_runs_job_type"), "job_runs", ["job_type"], unique=False)
    op.create_index(op.f("ix_job_runs_status"), "job_runs", ["status"], unique=False)
    op.create_index(op.f("ix_job_runs_target_id"), "job_runs", ["target_id"], unique=False)

    op.create_table(
        "narrative_clusters",
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("strength", sa.Float(), nullable=False),
        sa.Column("sentiment", sa.String(length=40), nullable=True),
        sa.Column("trend_direction", sa.String(length=40), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_narrative_clusters")),
    )
    op.create_index(op.f("ix_narrative_clusters_label"), "narrative_clusters", ["label"], unique=False)
    op.create_index(
        "ix_narrative_clusters_strength_trend",
        "narrative_clusters",
        ["strength", "trend_direction"],
        unique=False,
    )
    op.create_index(op.f("ix_narrative_clusters_sentiment"), "narrative_clusters", ["sentiment"], unique=False)

    op.create_table(
        "raw_documents",
        sa.Column("source_name", sa.String(length=120), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("content_hash", sa.String(length=128), nullable=False),
        sa.Column("ingestion_metadata", sa.JSON(), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_raw_documents")),
        sa.UniqueConstraint("content_hash", name="uq_raw_documents_content_hash"),
    )
    op.create_index(op.f("ix_raw_documents_content_hash"), "raw_documents", ["content_hash"], unique=False)
    op.create_index(op.f("ix_raw_documents_published_at"), "raw_documents", ["published_at"], unique=False)
    op.create_index(op.f("ix_raw_documents_source_name"), "raw_documents", ["source_name"], unique=False)

    op.create_table(
        "financial_events",
        sa.Column("raw_document_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("topic", sa.String(length=120), nullable=True),
        sa.Column("sentiment", sa.String(length=40), nullable=True),
        sa.Column("importance", sa.Integer(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["raw_document_id"], ["raw_documents.id"], name=op.f("fk_financial_events_raw_document_id_raw_documents")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_financial_events")),
    )
    op.create_index(op.f("ix_financial_events_occurred_at"), "financial_events", ["occurred_at"], unique=False)
    op.create_index(op.f("ix_financial_events_raw_document_id"), "financial_events", ["raw_document_id"], unique=False)
    op.create_index(op.f("ix_financial_events_sentiment"), "financial_events", ["sentiment"], unique=False)
    op.create_index(op.f("ix_financial_events_title"), "financial_events", ["title"], unique=False)
    op.create_index(op.f("ix_financial_events_topic"), "financial_events", ["topic"], unique=False)
    op.create_index("ix_financial_events_topic_sentiment", "financial_events", ["topic", "sentiment"], unique=False)

    op.create_table(
        "embeddings",
        sa.Column("event_id", sa.String(), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("vector", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["financial_events.id"], name=op.f("fk_embeddings_event_id_financial_events")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_embeddings")),
    )
    op.create_index(op.f("ix_embeddings_event_id"), "embeddings", ["event_id"], unique=False)

    op.create_table(
        "event_entities",
        sa.Column("event_id", sa.String(), nullable=False),
        sa.Column("entity_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], name=op.f("fk_event_entities_entity_id_entities")),
        sa.ForeignKeyConstraint(["event_id"], ["financial_events.id"], name=op.f("fk_event_entities_event_id_financial_events")),
        sa.PrimaryKeyConstraint("event_id", "entity_id", name=op.f("pk_event_entities")),
    )

    op.create_table(
        "narrative_events",
        sa.Column("narrative_id", sa.String(), nullable=False),
        sa.Column("event_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["financial_events.id"], name=op.f("fk_narrative_events_event_id_financial_events")),
        sa.ForeignKeyConstraint(["narrative_id"], ["narrative_clusters.id"], name=op.f("fk_narrative_events_narrative_id_narrative_clusters")),
        sa.PrimaryKeyConstraint("narrative_id", "event_id", name=op.f("pk_narrative_events")),
    )


def downgrade() -> None:
    op.drop_table("narrative_events")
    op.drop_table("event_entities")
    op.drop_index(op.f("ix_embeddings_event_id"), table_name="embeddings")
    op.drop_table("embeddings")
    op.drop_index("ix_financial_events_topic_sentiment", table_name="financial_events")
    op.drop_index(op.f("ix_financial_events_topic"), table_name="financial_events")
    op.drop_index(op.f("ix_financial_events_title"), table_name="financial_events")
    op.drop_index(op.f("ix_financial_events_sentiment"), table_name="financial_events")
    op.drop_index(op.f("ix_financial_events_raw_document_id"), table_name="financial_events")
    op.drop_index(op.f("ix_financial_events_occurred_at"), table_name="financial_events")
    op.drop_table("financial_events")
    op.drop_index(op.f("ix_raw_documents_source_name"), table_name="raw_documents")
    op.drop_index(op.f("ix_raw_documents_published_at"), table_name="raw_documents")
    op.drop_index(op.f("ix_raw_documents_content_hash"), table_name="raw_documents")
    op.drop_table("raw_documents")
    op.drop_index(op.f("ix_narrative_clusters_sentiment"), table_name="narrative_clusters")
    op.drop_index("ix_narrative_clusters_strength_trend", table_name="narrative_clusters")
    op.drop_index(op.f("ix_narrative_clusters_label"), table_name="narrative_clusters")
    op.drop_table("narrative_clusters")
    op.drop_index(op.f("ix_job_runs_target_id"), table_name="job_runs")
    op.drop_index(op.f("ix_job_runs_status"), table_name="job_runs")
    op.drop_index(op.f("ix_job_runs_job_type"), table_name="job_runs")
    op.drop_table("job_runs")
    op.drop_index(op.f("ix_entities_symbol"), table_name="entities")
    op.drop_index(op.f("ix_entities_name"), table_name="entities")
    op.drop_index(op.f("ix_entities_entity_type"), table_name="entities")
    op.drop_table("entities")
