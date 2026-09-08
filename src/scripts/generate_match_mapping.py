import asyncio
import httpx
import csv
from pathlib import Path


async def build_mapping_csv(api_key: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://v3.football.api-sports.io/fixtures",
            params={"league": 4, "season": 2024},
            headers={"x-apisports-key": api_key}
        )

    resp.raise_for_status()
    data = resp.json()

    if data.get("errors"):
        raise RuntimeError(f"API error: {data['errors']}")

    fixtures = data["response"]

    if not fixtures:
        raise RuntimeError("No fixtures returned — check league/season params or API key/plan")

    print(f"Fetched {len(fixtures)} fixtures")
    if len(fixtures) != 51:
        print(f"WARNING: expected 51 Euro 2024 matches, got {len(fixtures)} — check for duplicates or missing games")

    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    out_path = PROJECT_ROOT / "data" / "reference" / "match_id_mapping.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["match_id", "api_football_fixture_id", "statsbomb_match_id", "statsbomb_competition_id", "statsbomb_season_id"])
        for i, fx in enumerate(fixtures, start=1):
            writer.writerow([i, fx["fixture"]["id"], "", "55", "282"])

    print(f"Wrote {len(fixtures)} rows to {out_path}")


if __name__ == "__main__":
    api_key = Path("api_key.txt").read_text().strip()
    asyncio.run(build_mapping_csv(api_key))