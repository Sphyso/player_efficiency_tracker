from enum import Enum

class EventType(Enum):
    GOAL = auto()
    ASSIST = auto()
    CORNER = auto()
    CARD = auto()
    VAR = auto()
    FREEKICK = auto()
    PENALTY = auto()