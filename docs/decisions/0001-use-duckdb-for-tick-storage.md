# ADR 0001: Use DuckDB for tick storage

**Date:** 4/21/26
**Status:** Accepted

## Context

We need to store tick-level Bazaar data — 600+ items polled every 20 seconds, producing ~2.5 million rows per day. The storage layer must support:

1. Fast append during live ingestion.
2. Fast analytical queries during backtesting (scans over millions of rows with aggregations).
3. Zero operational overhead for a solo developer.
4. A file-based format that can be backed up trivially.

## Options considered

- **PostgreSQL** — industry standard, but requires running a server process, managing users, configuring connections. Overkill for a single-developer project with analytical workloads.
- **SQLite** — file-based and simple, but row-store design is poor for analytical queries over millions of rows.
- **DuckDB** — file-based like SQLite, but column-store with vectorized execution. Designed for exactly this workload (OLAP on a single machine).
- **Parquet files + pandas** — fast reads, but no transactional append; concurrent writes are painful.

## Decision

Use DuckDB. It combines SQLite's zero-ops simplicity with columnar performance for analytical queries.

## Consequences

- **Positive:** No server to manage. Excellent analytical performance. SQL interface. Integrates with pandas and Python natively.
- **Negative:** Smaller ecosystem than Postgres. Some advanced SQL features may be missing. If we ever need multi-writer concurrency, we will need to migrate.
- **Migration path:** DuckDB can read and write Parquet natively; if we ever outgrow it, we export to Parquet and move to a data-warehouse solution.