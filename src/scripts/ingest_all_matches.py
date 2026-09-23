import csv
import psycopg2  # swap for whatever connection pattern the rest of the project uses
from src.ingestion.dispatcher import get_matches

def load_all_match_ids(csv_path: str) -> list[int]:
    with open(csv_path) as f:
        return [int(row["match_id"]) for row in csv.DictReader(f)]

def get_already_ingested(conn) -> set[int]:
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT match_id FROM bronze.raw_matches")
        return {row[0] for row in cur.fetchall()}

if __name__ == "__main__":
    all_ids = load_all_match_ids("data/reference/match_id_mapping.csv")

    conn = psycopg2.connect(...)  # your actual connection details
    already_done = get_already_ingested(conn)
    conn.close()

    to_ingest = [m for m in all_ids if m not in already_done]
    print(f"{len(already_done)} already ingested, {len(to_ingest)} remaining")

    matches = get_matches(to_ingest)
    print(f"Done. {len(matches)} match records returned this run.")