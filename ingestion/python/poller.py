"""
poller.py — continuously polls the Hypixel Bazaar API and stores snapshots.

Usage:
    python poller.py                  # run forever, 20s interval
    python poller.py --once           # fetch once and exit
    python poller.py --dry-run        # fetch but don't write to DB
    python poller.py --interval 30    # poll every 30 seconds

Logs to stdout and to logs/poller.log.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import requests

BAZAAR_URL = "https://api.hypixel.net/v2/skyblock/bazaar"
TOP_N_LEVELS = 5
SCHEMA_PATH = Path("ingestion/python/schema.sql")
DEFAULT_DB_PATH = Path("data/raw/bazaar.duckdb")
LOG_PATH = Path("logs/poller.log")

log = logging.getLogger("poller")


def fetch_bazaar() -> dict:
    """Fetch the current Bazaar snapshot. Raises on HTTP error."""
    response = requests.get(BAZAAR_URL, timeout=10)
    response.raise_for_status()
    return response.json()


def parse_tick(data: dict) -> tuple[list[tuple], list[tuple]]:
    """
    Transform a raw Bazaar response into (tick_rows, order_book_rows)
    ready to pass to executemany.
    """
    ts = datetime.fromtimestamp(data["lastUpdated"] / 1000, tz=timezone.utc)
    products = data.get("products", {})

    tick_rows: list[tuple] = []
    order_book_rows: list[tuple] = []

    for product_id, product in products.items():
        status = product.get("quick_status") or {}
        tick_rows.append((
            ts,
            product_id,
            status.get("buyPrice"),
            status.get("sellPrice"),
            status.get("buyVolume"),
            status.get("sellVolume"),
            status.get("buyMovingWeek"),
            status.get("sellMovingWeek"),
            status.get("buyOrders"),
            status.get("sellOrders"),
        ))

        for side, key in (("buy", "buy_summary"), ("sell", "sell_summary")):
            for level, entry in enumerate(product.get(key, [])[:TOP_N_LEVELS], start=1):
                order_book_rows.append((
                    ts,
                    product_id,
                    side,
                    level,
                    entry.get("pricePerUnit"),
                    entry.get("amount"),
                    entry.get("orders"),
                ))

    return tick_rows, order_book_rows


def write_tick(
    conn: duckdb.DuckDBPyConnection,
    tick_rows: list[tuple],
    order_book_rows: list[tuple],
) -> None:
    """Insert one tick's worth of rows into the DB."""
    # Hypixel's lastUpdated only advances every few seconds, so consecutive
    # polls often carry the same ts. INSERT OR IGNORE skips the duplicates
    # rather than raising on the primary-key collision.
    conn.execute("BEGIN")
    try:
        if tick_rows:
            conn.executemany(
                "INSERT OR IGNORE INTO ticks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                tick_rows,
            )
        if order_book_rows:
            conn.executemany(
                "INSERT OR IGNORE INTO order_book VALUES (?, ?, ?, ?, ?, ?, ?)",
                order_book_rows,
            )
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


def run_once(conn: duckdb.DuckDBPyConnection | None, dry_run: bool) -> None:
    """Fetch one snapshot, parse, and write (unless dry-run)."""
    try:
        data = fetch_bazaar()
    except requests.RequestException as e:
        log.warning("fetch failed: %s", e)
        return

    if not data.get("success"):
        log.warning("API returned success=False; skipping")
        return

    tick_rows, order_book_rows = parse_tick(data)
    snapshot_ts = tick_rows[0][0] if tick_rows else "?"
    log.info(
        "snapshot %s — %d products, %d order-book rows%s",
        snapshot_ts,
        len(tick_rows),
        len(order_book_rows),
        " (dry-run)" if dry_run or conn is None else "",
    )

    if dry_run or conn is None:
        return

    write_tick(conn, tick_rows, order_book_rows)


def run_forever(
    conn: duckdb.DuckDBPyConnection | None,
    interval: int,
    dry_run: bool,
) -> None:
    """Poll on a fixed interval until interrupted."""
    log.info("polling every %ds (dry_run=%s)", interval, dry_run)
    while True:
        start = time.monotonic()
        try:
            run_once(conn, dry_run)
        except Exception:
            log.exception("unhandled error in run_once")
        elapsed = time.monotonic() - start
        time.sleep(max(0.0, interval - elapsed))


def setup_logging() -> logging.Logger:
    """Configure logging to stdout and file."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # Clear any handlers a previous import installed (e.g. in tests/REPL).
    root.handlers.clear()

    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(fmt)
    root.addHandler(stream)

    file_handler = logging.FileHandler(LOG_PATH)
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    return log


def setup_db(db_path: Path) -> duckdb.DuckDBPyConnection:
    """Open the DuckDB connection and apply schema.sql."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(db_path))
    conn.execute(SCHEMA_PATH.read_text())
    return conn


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="fetch once and exit")
    parser.add_argument("--dry-run", action="store_true", help="fetch but don't write")
    parser.add_argument("--interval", type=int, default=20, help="seconds between polls")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="DuckDB file path")
    args = parser.parse_args()

    setup_logging()

    conn: duckdb.DuckDBPyConnection | None = None
    if not args.dry_run:
        conn = setup_db(args.db)
        log.info("opened DB at %s", args.db)

    try:
        if args.once:
            run_once(conn, args.dry_run)
        else:
            run_forever(conn, args.interval, args.dry_run)
    except KeyboardInterrupt:
        log.info("interrupted, exiting")
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    main()
