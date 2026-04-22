# ADR 0002: Bazaar API data model — what we're actually ingesting

**Date:** 4/22/26
**Status:** Accepted

## Context

Before designing the ingestion schema, we need to document our understanding
of what the Hypixel Bazaar API actually returns, so future decisions (schema
design, feature engineering, strategy signals) are grounded in the real data
shape rather than assumptions.

## Observed data shape

The endpoint `GET https://api.hypixel.net/v2/skyblock/bazaar` returns a JSON
object with:

- `success` (boolean) — whether the call succeeded.
- `lastUpdated` (int, ms since epoch) — the snapshot timestamp.
- `products` (object) — a map from product ID to per-product data.

Each product contains:

- `product_id` (string) — e.g. `ENCHANTED_COCOA`, `INK_SACK:3`.
- `sell_summary` (array) — top sell orders (someone offering to sell *to* us),
  sorted best price first. Each has `amount`, `pricePerUnit`, `orders`.
- `buy_summary` (array) — top buy orders (someone offering to buy *from* us),
  sorted best price first. Same fields.
- `quick_status` (object) — aggregate stats including `sellPrice`, `buyPrice`,
  `sellVolume`, `buyVolume`, `sellMovingWeek`, `buyMovingWeek`, `sellOrders`,
  `buyOrders`.

## Key observations

1. **Naming convention is from the Bazaar's perspective.** `sell_summary`
   lists orders where someone else is selling — so if *we* want to buy at
   market, we cross the `sell_summary` side. This is the opposite of the
   convention in traditional exchanges ("bid" = buy interest, "ask" = sell
   interest). Internal code should rename consistently to avoid confusion.

2. **Spreads can be negative.** On liquid items, `buyPrice > sellPrice` is
   common, meaning a buy order is listed above a sell order. After the
   Bazaar's 1.25% tax, these inversions are rarely arbitrageable.

3. **Volumes span multiple orders of magnitude.** Liquid items show
   `sellMovingWeek` in the hundreds of millions; illiquid items show a few
   thousand. Strategy design must branch on liquidity tier.

4. **The `orders` field per price level indicates concentration.** A level
   with `amount=50000, orders=1` is one large actor; `amount=50000, orders=50`
   is retail. This is a signal for manipulation detection later.

5. **Product IDs include special characters** (e.g. `INK_SACK:3`). The schema
   must treat the ID as an opaque string, not parse it.

## Decision

Our internal data model will store **one row per product per poll tick**,
flattening `quick_status` into columns and preserving the top-N buy and sell
summary entries (likely N=5 or N=10). The full `products` payload will *not*
be stored verbatim; we'll extract the fields we need.

## Consequences

- **Positive:** compact storage (~200 bytes per product per tick), fast
  analytical queries, schema matches how strategies actually use the data.
- **Negative:** if we later discover we need a field we didn't extract, we
  can't reconstruct it from historical storage. Mitigation: keep a rolling
  raw-JSON archive (e.g., last 24 hours of raw responses) as a safety net
  during the first month.
- **Revisit:** after one week of ingestion, inspect which fields are actually
  useful. Drop unused columns; raise the raw-archive window if we've hit it.