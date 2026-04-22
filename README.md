# HyperCycle

**A quantitative trading system for the Hypixel Skyblock Bazaar, built with production-grade reproducibility guarantees.**

HyperCycle ingests real-time order-book data from the Hypixel Bazaar API, reconstructs a synthetic limit order book in a C++ hot path, and runs statistical strategies (cointegration-based pair trades, regime-switching mean reversion, manipulation detection) against it. Performance is evaluated with walk-forward validation against a cryptographically-sealed holdout set.

> 🚧 **Status:** Under active development. See [`docs/journal.md`](docs/journal.md) for daily progress. Follow the commit history for the full build story from empty folder to deployed system.

---

## For Different Readers

- **Systems / Infrastructure engineers** — see `ingestion/cpp/` and `docs/latency.md` for the C++ hot path, lock-free IPC, and latency profiling.
- **ML engineers / researchers** — see `strategy/` and `docs/reproducibility.md` for the point-in-time feature architecture and multiple-testing-corrected evaluation.
- **Quant researchers** — see `docs/strategies.md` and the live out-of-sample performance chart below.
- **Generalist SWE** — see `docs/architecture.md` for the system diagram and deployment story.

---

## Live System

- **Dashboard:** *[deploy target — coming Week 11]*
- **Out-of-sample P&L since deploy:** *[chart embed]*
- **Uptime:** *[badge]*
- **Most recent holdout evaluation:** *[signed log entry]*

---

## Epistemic Infrastructure

This system is designed so that its author cannot accidentally or intentionally fool themselves. Specifically:

- The holdout set is AES-encrypted; every decryption is logged to an append-only, git-committed record.
- Features are enforced point-in-time at the type level — accessing future data raises an exception.
- All backtests are logged immutably via a pre-commit hook; the final report applies a Bonferroni correction over total experiments run.
- Transaction costs (1.25% Bazaar tax), slippage, and fill probability cannot be disabled.
- A "Live Paper Wall" process runs the strategy forward on data that did not exist at deploy time; this is the gold-standard out-of-sample signal.

See `docs/reproducibility.md` for details.

---

## Architecture

*[System diagram — coming Week 2]*

**Stack:** C++20, Python 3.12, DuckDB, FastAPI, Next.js, Three.js, Docker.

---

## Running Locally

*[To be filled in — coming Week 11]*

---

## Author

Built by a UCLA freshman as an exercise in unorthodox engineering. See the commit log for the full build story.