import pandas as pd
from pathlib import Path
from statsbombpy import sb

# Config: values used to get competition/season/match
COMPETITION_ID = 43     # FIFA World Cup
SEASON_ID = 106         # 2022
MATCH_ID = 3857298      # Portugal vs Ghana

RAW_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

def get_competitions() -> pd.DataFrame:
    return sb.competitions()

def get_matches(competition_id, season_id) -> pd.DataFrame:
    matches = sb.matches(competition_id = competition_id, season_id = season_id)
    matches["score"] = matches["home_score"].astype(str) + " - " + matches["away_score"].astype(str)
    return matches[["match_id", "match_date", "home_team", "away_team", "score"]].sort_values(by="match_date")

def get_match_events(match_id) -> pd.DataFrame:
    return sb.events(match_id = match_id)

def save_raw_events(events, match_id) -> Path:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DATA_DIR / f"match_{match_id}_events.json"
    events.to_json(out_path, orient="records", indent=2)
    return out_path

def main():
    events = get_match_events(MATCH_ID)
    out_path = save_raw_events(events, MATCH_ID)
    print(f"Saved {len(events)} events to {out_path}")

if __name__ == "__main__":
    main()