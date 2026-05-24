# Day 7 Reflection

## What Makes Ingestion Reliable

Reliable ingestion is not just "can the API accept a POST request?"

Reliable ingestion means the system can explain:

- where a document came from
- whether it was already seen before
- what raw source text was stored
- what structured event was created
- what job recorded the ingestion work
- which parts of the document still need enrichment

The current implementation does this through `RawDocument`, `FinancialEvent`, `JobRun`, content hashing, source metadata, and tests for both manual and RSS ingestion.

## Why Shared Ingestion Logic Matters

Manual input and RSS input now converge on `_ingest_document()`.

That is important because external sources should not each invent their own storage behavior. A future SEC connector, news API connector, or Reddit connector should only translate source-specific payloads into the common internal ingestion shape.

The shared path keeps deduplication, raw document creation, event shell creation, and job recording consistent.

## What Is Still Fragile

Several parts are intentionally still simple:

- The RSS connector runs synchronously inside the API request.
- There is no queue yet.
- There is no retry/backoff policy yet.
- There is no rate-limit handling yet.
- There is no source fetch history yet.
- One raw document currently creates one event shell.
- The event shell is not enriched with topic, sentiment, importance, entities, or embeddings.

These are acceptable at this stage because the point of Days 5-7 was to create and verify the ingestion foundation. Day 8 should start moving processing into workers.

## Day 7 Decision

Keep ingestion source normalization simple and traceable. Do not add AI interpretation into ingestion. The next major architecture improvement should be queue-backed workers for enrichment and source refresh jobs.
