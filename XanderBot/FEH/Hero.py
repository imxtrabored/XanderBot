import asyncio
from enum import Enum

class Color(Enum):
    """Enum for each unit color"""
    RED = 0
    BLUE = 1
    GREEN = 2
    COLORLESS = 3

class WeaponType(Enum):
    """Enum for each weapon type"""
    RSWORD = 0
    RTOME = 1
    RBREATH = 2
    BLANCE = 3
    BTOME = 4
    BBREATH = 5
    GAXE = 6
    GTOME = 7
    GBREATH = 8
    CBOW = 9
    CDAGGER = 10
    CSTAFF = 11
    CBREATH = 12
    RBOW = 13
    BBOW = 14
    GBOW = 15
    RDAGGER = 16
    BDAGGER = 17
    GDAGGER = 18

class MoveType(Enum):
    """Enum for each movement type"""
    INFANTRY = 0
    ARMOR = 1
    CAVALRY = 2
    FLYING = 3

class TomeType(Enum):
    """Enum for tome elements, UNUSED"""
    NONE = 0
    FIRE = 1
    THUNDER = 2
    WIND = 3
    DARK = 4
    LIGHT = 5

class LegendElement:
    """Enum for elements of Legendary Heroes"""
    NONE = 0
    FIRE = 1
    WATER = 2
    WIND = 3
    EARTH = 4

class LegendBoost:
    """Enum for each stat boost from Legendary Heroes"""
    NONE = 0
    ATK = 1
    SPD = 2
    DEF = 3
    RES = 4

class Hero(object):
    """Representation of a unit in FEH"""

    @classmethod
    async def create(cls, heroName = "null"):
        """Temporary init; will replace with sqlite lookup"""
        self = Hero()

        #initialize unit name
        self.name = "Null"
        self.epithet = "Null Hero"
        self.BVID = 0x0000

        #initialize basic unit attributes
        self.color = Color.RED
        self.weaponType = WeaponType.RSWORD
        self.moveType = MoveType.INFANTRY
        self.tomeType = TomeType.NONE
        self.rarity = 5

        #initialize unit stats
        self._baseHP = 20
        self._baseAtk = 10
        self._baseSpd = 10
        self._baseDef = 4
        self._baseRes = 4
        self._baseTotal = (self._baseHP + self._baseAtk + self._baseSpd
                           + self._baseDef + self._baseRes)

        self._growthHP = 50
        self._growthAtk = 55
        self._growthSpd = 70
        self._growthDef = 60
        self._growthRes = 60
        self._growthTotal = (self._growthHP + self._growthAtk
                             + self._growthSpd + self._growthDef
                             + self._growthRes)

        self._maxHP = 40
        self._maxAtk = 34
        self._maxSpd = 40
        self._maxDef = 30
        self._maxRes = 30
        self._maxTotal = (self._maxHP + self._maxAtk + self._maxSpd
                          + self._maxDef + self._maxRes)

        #stat calc stuff
        self.isVeteran = False
        self.isTrainee = False
        self.isDancer = False
        self.generation = 2

        #legendary hero stuff
        self.isLegend = False
        self.legendElement = LegendElement.NONE
        self.legendBoost = LegendBoost.NONE

        #fluff
        self.artPortrait = ''
        self.artAttack = ''
        self.artSpecial = ''
        self.artDamaged = ''
        self.artist = ''
        self.voEN = ''
        self.voJP = ''

        #bonus units
        self.isArenaBonus = False
        self.isAetherBonus = False
        self.isAetherBonusNext = False
        self.isTempestBonus = False

        #other
        self.isStory = False
        self.isSeasonal = False
        self.isGrail = False

        return(self)


