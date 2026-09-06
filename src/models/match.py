from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from src.models.event_type import EventType 


class TeamInfo(BaseModel):
    team_id: int = Field(gt=0)
    team_name: str


class PlayerMatchStats(BaseModel):
    player_id: int = Field(gt=0)
    player_name: str
    team_id: int = Field(gt=0)
    match_id: int = Field(gt=0)
    is_substitute: bool
    minutes_played: Optional[int] = None
    position: Optional[str] = None
    goals_total: Optional[int] = None
    assists: Optional[int] = None
    yellow_cards: int = 0
    red_cards: int = 0
    fouls_committed: Optional[int] = None


class MatchEvent(BaseModel):
    event_type: EventType
    team_id: int = Field(gt=0)
    match_id: int = Field(gt=0)
    time_elapsed: int = Field(ge=0, le=130)
    time_extra: Optional[int] = None
    primary_player_id: Optional[int] = None
    secondary_player_id: Optional[int] = None

    @field_validator('primary_player_id', 'secondary_player_id', mode='before')
    @classmethod
    def validate_player_ids(cls, v):
        """If player_id is provided, it must be > 0."""
        if v is not None and v <= 0:
            raise ValueError('player_id must be > 0 when provided')
        return v


class Match(BaseModel):
    match_id: int = Field(gt=0)
    match_date: datetime
    venue_name: Optional[str] = None
    tournament_stage: str
    home_team: TeamInfo
    away_team: TeamInfo
    players: List[PlayerMatchStats] = Field(default_factory=list)
    events: List[MatchEvent] = Field(default_factory=list)