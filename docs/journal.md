# Development Journal

A running log of what I built, what I tried, what broke, and what I learned. Updated daily.

---

## Day 1

**Date:** 4/21/26

**Goal:** Set up the project skeleton, write the README, make the first commit.

**What I did:**
- Installed Homebrew, Python 3.12, DuckDB, CMake, tmux, jq.
- Configured VS Code with Python, C/C++, GitLens, and TOML extensions.
- Created the `HyperCycle` GitHub repo.
- Built the full directory skeleton (ingestion, strategy, research, web, infra).
- Wrote a README-driven-development draft with four audience entry points.
- Set up `.gitignore` covering Python, C++, data, secrets, and OS artifacts.

**What I learned:**
- `mkdir -p` creates parent directories as needed; `&&` chains commands so each runs only if the previous succeeded.
- `find -type d -empty -exec touch {}/.gitkeep \;` is how you force git to track empty folders.
- README-driven development means writing the README as if the project is done, then building toward it.
- Architecture Decision Records (ADRs) are short docs that record *why* a technical choice was made — a senior-engineer habit.

**What's next:**
- Day 2: Read the Hypixel Bazaar API docs. Write ADR 0002 on the data model. Build a ~20-line script that fetches one item and prints it.

---

## Day 2

**Date:** 4/22/26

**Goal:** Understand the Hypixel Bazaar API data shape. Write a probe script. Document findings in an ADR.

**What I did:**
- Explored the `/v2/skyblock/bazaar` endpoint with `curl` + `jq`. Learned how to select nested fields and how to quote special characters in jq.
- Set up a project-local Python virtual environment (`.venv`) with `requests` and `python-dotenv`.
- Pinned dependencies to `requirements.txt` via `pip freeze`.
- Wrote `ingestion/python/probe.py` — a one-shot script that fetches the Bazaar, summarizes a single product, and handles errors gracefully.
- Wrote ADR 0002 documenting the observed data model.

**What I learned:**
- jq's selector syntax: `.products.ENCHANTED_COCOA.quick_status`. Special characters need quoting: `.products."INK_SACK:3"`.
- `sell_summary` means "someone is selling to us," so we cross it when buying at market. Counterintuitive naming — flipped from traditional exchange conventions.
- Bazaar spreads can go negative on liquid items. After the 1.25% tax, most inversions aren't arbitrage.
- Virtual environments isolate per-project Python. `source .venv/bin/activate` must be run in every new terminal session.
- `pip freeze > requirements.txt` is the basic reproducibility step most students skip.
- The `raise_for_status()` pattern in `requests` — always assert HTTP success before trusting the response body.

**What's next:**
- Day 3: Design the DuckDB schema. Write the real poller that loops every 20 seconds and writes ticks to disk. Start the first continuous data collection run.

