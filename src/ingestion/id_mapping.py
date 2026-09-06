from pathlib import Path
import pandas as pd

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