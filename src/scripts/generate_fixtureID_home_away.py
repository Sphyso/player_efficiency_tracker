import asyncio
import httpx
import csv
import os
from pathlib import Path
from dotenv import load_dotenv


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

    out_path = Path("data/reference/fixture_teams.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fixture_id", "home_team", "away_team"])
        for fx in fixtures:
            fixture_id = fx["fixture"]["id"]
            home_team = fx["teams"]["home"]["name"]
            away_team = fx["teams"]["away"]["name"]
            writer.writerow([fixture_id, home_team, away_team])
    print(f"Wrote {len(fixtures)} rows to {out_path}")

if __name__ == "__main__":
    load_dotenv()
    api_key = os.environ["API_KEY"]
    asyncio.run(build_mapping_csv(api_key))