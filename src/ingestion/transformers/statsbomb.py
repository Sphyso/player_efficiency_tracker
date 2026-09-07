import datetime
from pathlib import Path

from models.event_type import EventType
from src.models.match import Match, TeamInfo, PlayerMatchStats, MatchEvent
from src.ingestion.id_mapping import resolve_canonical_match_id

def ingest_offline(json_path: Path) -> list[Match]:
    """
    Load StatsBomb JSON offline fixture and transform to canonical Match.
    
    INPUT: StatsBomb JSON file
    OUTPUT: list[Match] with canonical match_id
    """
    import json
    
    with open(json_path) as f:
        raw_data = json.load(f)
    
    # Extract the StatsBomb match_id (external ID)
    statsbomb_match_id = raw_data["match_id"]
    
    # Convert to canonical ID via CSV lookup
    canonical_match_id = resolve_canonical_match_id(statsbomb_match_id)
    
    # Extract Match-level fields
    match = Match(
        match_id = canonical_match_id,
        match_date = datetime.fromisoformat(raw_data["match_date"]),
        venue_name = raw_data.get("venue"),
        tournament_stage = raw_data.get("competition_stage", "Group Stage"),
        home_team = TeamInfo(
            team_id = raw_data["home_team"]["team_id"],
            team_name = raw_data["home_team"]["team_name"]
        ),
        away_team = TeamInfo(
            team_id = raw_data["away_team"]["team_id"],
            team_name = raw_data["away_team"]["team_name"]
        ),
        players = _extract_statsbomb_players(raw_data, canonical_match_id),
        events = _extract_statsbomb_events(raw_data, canonical_match_id)
    )
    
    return [match]


def _extract_statsbomb_players(raw_data: dict, canonical_match_id: int) -> list[PlayerMatchStats]:
    """Extract player stats from StatsBomb JSON."""
    players = []
    for player_data in raw_data.get("players", []):
        player = PlayerMatchStats(
            match_id = canonical_match_id,
            player_id = player_data["player_id"],
            player_name = player_data["player_name"],
            team_id = player_data["team_id"],
            is_substitute = player_data.get("type", {}).get("name") == "Substitute",
            minutes_played = player_data.get("duration"),
            position = player_data.get("position"),
            goals_total = player_data.get("statistics", {}).get("goals", 0),
            assists = player_data.get("statistics", {}).get("assists", 0),
            yellow_cards = player_data.get("statistics", {}).get("yellow_card", 0),
            red_cards = player_data.get("statistics", {}).get("red_card", 0),
            fouls_committed = player_data.get("statistics", {}).get("fouls_committed")
        )
        players.append(player)
    return players


def _extract_statsbomb_events(raw_data: dict, canonical_match_id: int) -> list[MatchEvent]:
    """Extract match events from StatsBomb JSON."""
    events = []
    for event_data in raw_data.get("events", []):
        try:
            event = MatchEvent(
                match_id = canonical_match_id,
                event_type = EventType(event_data["type"]["name"]),  # "Shot", "Pass", etc.
                team_id = event_data["team"]["team_id"],
                time_elapsed = int(event_data["minute"]),
                time_extra = event_data.get("second"),
                primary_player_id = event_data.get("player", {}).get("id"),
                secondary_player_id = event_data.get("receiver", {}).get("id")
            )
            events.append(event)
        except ValueError:
            # Event type not in EventType enum, skip it
            continue
    return events