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

def main():
    events = get_match_events(MATCH_ID)
    matches = get_matches(COMPETITION_ID, SEASON_ID)
    print(matches)

if __name__ == "__main__":
    main()