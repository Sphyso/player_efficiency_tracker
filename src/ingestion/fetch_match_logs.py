import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

RAW_DATA_DIR = Path("data/raw")

def fetch_sample_match_log():
    """
    Simulates fetching raw match logs (lineups, cards, minutes)
    and landing them in the raw S3/local data lake directory.
    """
    print("🚀 Initializing Match Log Ingestion...")


    # Mock payload simulating what a soccer API returns
    mock_payload = {
        "match_id": "WC2026_FINAL_01",
        "stage": "Final",
        "teams": {
            "home": "Argentina",
            "away": "Spain"
        },
        "player_events": [
            {
                "player_id": 101,
                "player_name": "Julian Alvarez",
                "is_starter": True,
                "minutes_played": 78,
                "goals": 0,
                "assists": 0,
                "yellow_cards": 0,
                "red_cards": 0,
                "fouls_committed": 2
            },
            {
                "player_id": 102,
                "player_name": "Lautaro Martinez",
                "is_starter": False,
                "minutes_played": 12,
                "goals": 0,
                "assists": 0,
                "yellow_cards": 1,
                "red_cards": 0,
                "fouls_committed": 1
            }
        ]
    }

    # Ensure landing directory exists
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    output_path = RAW_DATA_DIR / f"{mock_payload['match_id']}.json"
    
    with open(output_path, "w") as f:
        json.dump(mock_payload, f, indent=2)
        
    print(f"✅ Successfully landed raw match log to: {output_path}")

if __name__ == "__main__":
    fetch_sample_match_log()