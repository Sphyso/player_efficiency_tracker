import json
from src.db import get_connection

_UPSERT_SQL = """
INSERT INTO bronze.raw_matches (match_id, fixture_id, raw_payload, ingested_at, source)
VALUES (%s, %s, %s, now(), %s)
ON CONFLICT (match_id)
DO UPDATE SET
    fixture_id  = EXCLUDED.fixture_id,
    raw_payload = EXCLUDED.raw_payload,
    ingested_at = EXCLUDED.ingested_at,
    source      = EXCLUDED.source;
"""

def upsert_raw_match(match_id: int, fixture_id: int, raw_payload: dict, source: str = "api_football") -> None:
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(_UPSERT_SQL, (match_id, fixture_id, json.dumps(raw_payload), source))
    finally:
        conn.close()