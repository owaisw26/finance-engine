# Alembic Migrations

Alembic tracks database schema changes for Finance Engine.

Common commands:

```bash
alembic upgrade head
alembic revision --autogenerate -m "describe change"
```

The first migration creates the core intelligence schema: raw documents, financial events, entities, embeddings, narrative clusters, job runs, and relationship tables.
