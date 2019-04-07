from enum import Enum, unique

@unique
class DragonflowerInc(Enum):
    INFANTRY = 1
    ARMOR    = 2
    CAVALRY  = 3
    FLIER    = 4
    DOWN     = 5

    @classmethod
    def get_type(cls, type):
        return cls(type.value)

@unique
class RarityInc(Enum):
    UP   = 1
    DOWN = 2
