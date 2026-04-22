"""
probe.py — a one-shot exploration script for the Hypixel Bazaar API.

Fetches the current Bazaar snapshot, parses it, and prints a clean summary
of a single chosen product. Not meant to be run continuously — use this to
understand the data shape before writing the real poller.

Usage:
    python probe.py                 # defaults to ENCHANTED_COCOA
    python probe.py ENCHANTED_DIAMOND
"""

import sys
import json
from datetime import datetime, timezone

import requests

BAZAAR_URL = "https://api.hypixel.net/v2/skyblock/bazaar"
DEFAULT_PRODUCT = "ENCHANTED_COCOA"


def fetch_bazaar() -> dict:
    """Fetch the current Bazaar snapshot. Returns the parsed JSON."""
    response = requests.get(BAZAAR_URL, timeout=10)
    response.raise_for_status()  # raises an exception on HTTP errors
    return response.json()


def summarize_product(data: dict, product_id: str) -> None:
    """Print a clean summary of a single product's market state."""
    products = data.get("products", {})
    if product_id not in products:
        print(f"❌ Product '{product_id}' not found. Available: {len(products)} products.")
        print(f"   First 10: {list(products.keys())[:10]}")
        return

    product = products[product_id]
    status = product["quick_status"]

    last_updated = datetime.fromtimestamp(
        data["lastUpdated"] / 1000, tz=timezone.utc
    )

    spread = status["sellPrice"] - status["buyPrice"]
    spread_pct = (spread / status["buyPrice"] * 100) if status["buyPrice"] else 0

    print(f"\n=== {product_id} ===")
    print(f"Snapshot time (UTC): {last_updated.isoformat()}")
    print(f"Best buy price (what sellers are asking): {status['sellPrice']:,.2f}")
    print(f"Best sell price (what buyers are offering): {status['buyPrice']:,.2f}")
    print(f"Spread: {spread:,.4f} coins  ({spread_pct:+.2f}%)")
    print(f"Sell-side volume: {status['sellVolume']:,} units across {status['sellOrders']} orders")
    print(f"Buy-side volume:  {status['buyVolume']:,} units across {status['buyOrders']} orders")
    print(f"Weekly volume: {status['sellMovingWeek']:,} sold / {status['buyMovingWeek']:,} bought")

    print("\nTop 3 sell orders (best prices sellers are offering):")
    for i, order in enumerate(product["sell_summary"][:3], 1):
        print(f"  {i}. {order['amount']:>8,} units @ {order['pricePerUnit']:,.2f}  ({order['orders']} orders)")

    print("\nTop 3 buy orders (best prices buyers are offering):")
    for i, order in enumerate(product["buy_summary"][:3], 1):
        print(f"  {i}. {order['amount']:>8,} units @ {order['pricePerUnit']:,.2f}  ({order['orders']} orders)")


def main() -> None:
    product_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PRODUCT
    print(f"🔎 Fetching Bazaar snapshot for {product_id}...")

    try:
        data = fetch_bazaar()
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        sys.exit(1)

    if not data.get("success"):
        print(f"❌ API returned success=False. Raw response:")
        print(json.dumps(data, indent=2)[:500])
        sys.exit(1)

    summarize_product(data, product_id)


if __name__ == "__main__":
    main()