CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS bronze.raw_matches (
    match_id     INTEGER PRIMARY KEY,
    fixture_id   INTEGER NOT NULL,
    raw_payload  JSONB NOT NULL,
    ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    source       TEXT NOT NULL DEFAULT 'api_football'
);