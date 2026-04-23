# ADR 0003: Storage and deployment phasing

**Date:** 4/22/26
**Status:** Accepted

## Context

Where does the tick data live during the project? The poller needs 24/7
operation to be useful, but cloud VM setup has real learning overhead
that could delay getting the ingestion pipeline working.

## Options considered

- **Local only:** laptop + caffeinate. Simple, free, but requires laptop-on.
- **Cloud VM (Oracle Free Tier):** 24/7, real deployment experience, ~3h setup.
- **Hybrid with cloud backup:** local + S3/B2 snapshots. Adds complexity
  without solving the laptop-on problem.

## Decision

Two-phase approach:

1. **Day 3 → Week 2:** run locally with `caffeinate`. Prove the poller works.
   Collect first week of data on laptop.
2. **Week 2 onward:** migrate to Oracle Cloud Free Tier ARM instance (4 cores,
   24 GB RAM, 200 GB storage). Re-run poller there under `systemd`. Laptop
   becomes dev-only; production runs in cloud.

## Consequences

- **Positive:** Day 3 isn't blocked on cloud setup. By Week 2 we have real
  Linux server ops experience before we need it for Week 11 deployment.
- **Negative:** data collected in week 1 lives on laptop only. Mitigation:
  copy the DuckDB file to the VM during migration — zero data loss.
- **Revisit:** if Oracle Free Tier is unavailable for any reason, fall back
  to Hetzner at €4/month, which is still within any student's budget.