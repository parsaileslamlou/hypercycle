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

