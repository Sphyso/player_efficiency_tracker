import os
from pathlib import Path
import pandas as pd
import csv

# Load once at module level
_MAPPING_TABLE = None

def _load_mapping():
    global _MAPPING_TABLE
    if _MAPPING_TABLE is None:
        mapping_path = Path(__file__).parent.parent.parent / "data/reference/match_id_mapping.csv"
        _MAPPING_TABLE = pd.read_csv(mapping_path)
    return _MAPPING_TABLE

def resolve_canonical_match_id(statsbomb_match_id: int) -> int:
    """
    Resolve a StatsBomb match_id to our canonical match_id.
    
    Args:
        statsbomb_match_id: The StatsBomb fixture ID from raw JSON
        
    Returns:
        The canonical match_id for our schema
        
    Raises:
        ValueError: If statsbomb_match_id is not in the mapping table
    """

    mapping = _load_mapping()
    row = mapping[mapping["statsbomb_match_id"] == statsbomb_match_id]
    
    if row.empty:
        raise ValueError(
            f"StatsBomb match_id {statsbomb_match_id} not found in mapping table. "
            f"Add it to data/reference/match_id_mapping.csv before ingesting."
        )
    
    return row.iloc[0]["match_id"]


def resolve_canonical_match_id_api_football(api_football_fixture_id: int) -> int:
    """
    Resolve an API-Football fixture_id to our canonical match_id.

    Args:
        api_football_fixture_id: The API-Football fixture ID from raw JSON

    Returns:
        The canonical match_id for our schema

    Raises:
        ValueError: If api_football_fixture_id is not in the mapping table
    """

    mapping = _load_mapping()
    row = mapping[mapping["api_football_fixture_id"] == api_football_fixture_id]

    if row.empty:
        raise ValueError(
            f"API-Football fixture_id {api_football_fixture_id} not found in mapping table. "
            f"Add it to data/reference/match_id_mapping.csv before ingesting."
        )

    return row.iloc[0]["match_id"]


def resolve_fixture_id(match_id: int) -> int:
    """canonical match_id -> api_football_fixture_id, for the live path."""
    with open("data/reference/match_id_mapping.csv") as f:
        for row in csv.DictReader(f):
            if int(row["match_id"]) == match_id:
                return int(row["api_football_fixture_id"])
    raise ValueError(f"No api_football_fixture_id mapped for match_id={match_id}")


def resolve_json_path(match_id: int) -> str:
    """canonical match_id -> local StatsBomb JSON path, for the offline path."""
    with open("data/reference/match_id_mapping.csv") as f:
        for row in csv.DictReader(f):
            if int(row["match_id"]) == match_id:
                statsbomb_match_id = row["statsbomb_match_id"]
                path = f"data/raw/statsbomb/{statsbomb_match_id}.json"
                if not os.path.isfile(path):
                    raise ValueError(
                        f"Derived path {path} does not exist for match_id={match_id}"
                    )
                return path
    raise ValueError(f"No statsbomb_match_id mapped for match_id={match_id}")