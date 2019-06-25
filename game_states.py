from enum import Enum, auto

class GameStates(Enum):
    PLAYERS_TURN = auto()
    ENEMY_TURN = auto()

    ROUNDS_PLAYERS_ACTION = auto()
    ROUNDS_ENEMY_ACTION = auto()

    BEGIN_DETAILED_COMBAT_ROUND = auto()

    MEDIATE_COMBAT_ROUNDS = auto()
