/*
 schema.sql: defines the DuckDB storage for Bazaar tick data.

 Two tables:
   - ticks: one row per product per poll (aggregate stats).
   - order_book: top 5 buy + sell price levels per product per poll.

 Indexes support the common query pattern: filter by product_id, scan over ts.
*/

CREATE TABLE IF NOT EXISTS ticks (
    ts TIMESTAMP,
    product_id VARCHAR,
    buy_price DOUBLE,
    sell_price DOUBLE,
    buy_volume BIGINT,
    sell_volume BIGINT,
    buy_moving_week BIGINT,
    sell_moving_week BIGINT,
    buy_orders INTEGER,
    sell_orders INTEGER,
    PRIMARY KEY (ts, product_id)
);

CREATE INDEX IF NOT EXISTS idx_ticks_product_ts ON ticks (product_id, ts);

CREATE TABLE IF NOT EXISTS order_book (
    ts TIMESTAMP,
    product_id VARCHAR,
    side VARCHAR,
    level SMALLINT,
    price DOUBLE,
    amount BIGINT,
    num_orders INTEGER,
    PRIMARY KEY (ts, product_id, side, level)
);

CREATE INDEX IF NOT EXISTS idx_order_book_product_ts_side ON order_book (product_id, ts, side);