from typing import List, Optional
from pydantic import BaseModel, Field

class TeamInfo(BaseModel):
    team_id: int
    team_name: str

class PlayerMatchStats(BaseModel):
    player_id: int
    player_name: str
    team_id: int
    is_substitute: bool
    minutes_played: int = 0
    position: str
    goals_total: int
    assists: int
    yellow_cards: int = 0
    red_cards: int = 0
    fouls_committed: int

class MatchEvent(BaseModel):
    event_type: Enum
    team_id: int
    time_elapsed: int
    time_extra: int
    primary_player_id: int
    secondary_player_id: int

class Match(BaseModel):
    match_id: int
    match_date: datetime
    venue_name: str
    tournament_stage: str
    home_team: TeamInfo
    away_team: TeamInfo
    players: [PlayerMatchStats]
    events: [MatchStats]
