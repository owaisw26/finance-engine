# Day 6 Reflection

## What Can Go Wrong With External Data Sources

External feeds are less controlled than manual input. They can fail, send malformed XML, omit fields, repeat old items, change source URLs, include HTML in descriptions, or publish irrelevant items.

That means connectors need defensive behavior:

- fetch with a timeout
- parse only usable items
- preserve source URLs and metadata
- deduplicate content
- return clear counts for created, duplicate, and skipped items
- avoid blocking the rest of the system when one source fails

The Day 6 connector handles a small but important slice of this: it fetches RSS XML, parses items, cleans descriptions, deduplicates through the shared content hash, and stores source metadata.

## How The Connector Behaves In Production

The current `POST /ingest/run` endpoint performs RSS ingestion synchronously. That is acceptable for the first connector because it proves the ingestion contract and storage path.

In production, this should move behind workers:

```text
scheduled source refresh
        |
        v
fetch RSS feed
        |
        v
store new RawDocuments
        |
        v
queue enrichment jobs
```

The API route can still exist for manual triggering, but scheduled ingestion should not depend on a user keeping an HTTP request open.

## Day 6 Decision

Build a generic RSS connector instead of hardcoding a single provider. This keeps the source layer flexible: any RSS-like financial feed can use the same ingestion path, and tests can validate behavior with local XML fixtures instead of live network calls.
