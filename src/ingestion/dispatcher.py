import asyncio
import time
import logging
from src.config import API_KEY
from src.ingestion.id_mapping import resolve_fixture_id
from src.ingestion.transformers.api_football import ingest_live
from src.models.match import Match

logger = logging.getLogger(__name__)

def get_matches(match_ids: list[int]) -> list[Match]:
    matches: list[Match] = []
    failed: list[int] = []

    for match_id in match_ids:
        try:
            fixture_id = resolve_fixture_id(match_id)
            result = asyncio.run(ingest_live(fixture_id, API_KEY))
            matches.extend(result)
            logger.info(f"Ingested match_id={match_id} (fixture_id={fixture_id})")
        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                logger.warning(f"Rate limited on match_id={match_id}, backing off 60s")
                time.sleep(60)
                try:
                    fixture_id = resolve_fixture_id(match_id)
                    result = asyncio.run(ingest_live(fixture_id, API_KEY))
                    matches.extend(result)
                    continue
                except Exception as retry_e:
                    logger.error(f"Retry failed for match_id={match_id}: {retry_e}")
            else:
                logger.error(f"Failed match_id={match_id}: {type(e).__name__}: {e}")
            failed.append(match_id)

    if failed:
        logger.warning(f"{len(failed)} matches failed: {failed}")

    return matches


# if __name__ == "__main__":
#     print(get_matches([34,46,47,48,49,50,51]))