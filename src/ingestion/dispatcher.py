import asyncio
from src.config import API_KEY
from src.ingestion.id_mapping import resolve_fixture_id
from src.ingestion.transformers.api_football import ingest_live
from src.models.match import Match


def get_matches(match_ids: list[int]) -> list[Match]:
    matches: list[Match] = []
    for match_id in match_ids:
        fixture_id = resolve_fixture_id(match_id)
        result = asyncio.run(ingest_live(fixture_id, API_KEY))
        matches.extend(result)
    return matches


if __name__ == "__main__":
    print(get_matches([2]))