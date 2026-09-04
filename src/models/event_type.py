from enum import Enum


class EventType(str, Enum):
    GOAL = "Goal"
    CARD = "Card"
    SUBSTITUTION = "subst"
    VAR = "Var"