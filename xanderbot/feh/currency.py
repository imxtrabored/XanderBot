from enum import Enum, unique

from feh.hero import MoveType

@unique
class Dragonflower(Enum):
    INFANTRY = 1
    ARMOR    = 2
    CAVALRY  = 3
    FLIER    = 4

    @classmethod
    def get_move(cls, move_type):
        return cls(move_type.value)
