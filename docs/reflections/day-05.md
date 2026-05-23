# Day 5 Reflection

## Why Ingestion Should Be Separate From Enrichment

Ingestion is responsible for capturing source material reliably. Enrichment is responsible for interpreting that material.

Those are different jobs.

If ingestion tries to summarize, classify, extract entities, embed, and cluster immediately, the API request becomes slow and fragile. A user should be able to submit a document even if an AI provider, embedding model, or worker is temporarily unavailable.

The Day 5 implementation keeps ingestion simple:

- accept a manual document
- normalize whitespace
- generate a content hash
- store a `RawDocument`
- create a minimal `FinancialEvent`
- record a successful manual ingestion `JobRun`

The later enrichment pipeline will add topic classification, sentiment, entity extraction, embeddings, and narrative clustering.

## Why Source Metadata Matters

Financial intelligence is only useful if it is traceable. The platform needs to know where information came from, when it was published, and what source-specific context was attached.

Source metadata lets the system answer:

- Which connector produced this document?
- Was this a seed document, RSS item, filing, or manual input?
- What URL or source ID supports this event?
- Can this document be deduplicated or reprocessed?

This is why `RawDocument` stores source name, URL, published timestamp, content hash, and metadata.

## Why Deduplication Matters

Financial sources often repeat the same information. RSS feeds can resend items, manual test data can be submitted twice, and multiple connectors can overlap.

The `content_hash` makes manual ingestion idempotent. If the same title and body are submitted again, the endpoint returns the existing document and event instead of creating duplicates.

That protects downstream systems. Without deduplication, search results, narrative strength, and event counts would be distorted by repeated copies of the same source material.

## Day 5 Decision

Create the first ingestion endpoint as `POST /ingest/manual`. It stores source truth and creates an initial event, but deliberately leaves expensive AI enrichment for later worker-driven pipeline stages.
