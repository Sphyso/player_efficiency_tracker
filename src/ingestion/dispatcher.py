import asyncio
from src.config import DATA_SOURCE, API_KEY
from src.ingestion.id_mapping import resolve_fixture_id, resolve_json_path
from src.ingestion.transformers.api_football import ingest_live
from src.ingestion.transformers.statsbomb import ingest_offline
from src.models.match import Match


def get_matches(match_ids: list[int]) -> list[Match]:
    matches: list[Match] = []
    for match_id in match_ids:
        if DATA_SOURCE == "live":
            fixture_id = resolve_fixture_id(match_id)
            result = asyncio.run(ingest_live(fixture_id, API_KEY))
        else:
            json_path = resolve_json_path(match_id)
            result = ingest_offline(json_path)
        matches.extend(result)
    return matches