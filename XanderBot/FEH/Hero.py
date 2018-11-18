import asyncio, sqlite3
from enum import Enum
from FEH.Skill import Skill

class Color(Enum):
    '''Enum for each unit color'''
    RED = 0
    BLUE = 1
    GREEN = 2
    COLORLESS = 3

class WeaponType(Enum):
    '''Enum for each weapon type'''
    R_SWORD = 0
    R_TOME = 1
    R_BREATH = 2
    B_LANCE = 3
    B_TOME = 4
    B_BREATH = 5
    G_AXE = 6
    G_TOME = 7
    G_BREATH = 8
    C_BOW = 9
    C_DAGGER = 10
    C_STAFF = 11
    C_BREATH = 12
    R_BOW = 13
    B_BOW = 14
    G_BOW = 15
    R_DAGGER = 16
    B_DAGGER = 17
    G_DAGGER = 18

class MoveType(Enum):
    '''Enum for each movement type'''
    INFANTRY = 0
    ARMOR = 1
    CAVALRY = 2
    FLYING = 3

class TomeType(Enum):
    '''Enum for tome elements, UNUSED'''
    NONE = 0
    FIRE = 1
    THUNDER = 2
    WIND = 3
    DARK = 4
    LIGHT = 5

class LegendElement:
    '''Enum for elements of Legendary Heroes'''
    NONE = 0
    FIRE = 1
    WATER = 2
    WIND = 3
    EARTH = 4

class LegendBoost:
    '''Enum for each stat boost from Legendary Heroes'''
    NONE = 0
    ATK = 1
    SPD = 2
    DEF = 3
    RES = 4

class SkillSet(object):
    """Contains learnable skills of a hero"""
    @staticmethod
    async def create(heroName = 'null'):
        self = SkillSet()

        self.weapon = [None] * 6
        self.assist = [None] * 6
        self.special = [None] * 6
        self.passiveA = [None] * 6
        self.passiveB = [None] * 6
        self.passiveC = [None] * 6
        self.weaponPrf = None

        self.weapon[1] = await Skill.create('null')
        self.weapon[2] = await Skill.create('null')
        self.weapon[3] = await Skill.create('null')
        self.weapon[5] = await Skill.create('null')

        return self

class Hero(object):
    '''Representation of a unit in FEH'''

    @staticmethod
    async def create(heroName = 'null'):
        '''Temporary init; will replace with sqlite lookup'''
        self = Hero()

        #initialize unit name
        self.name = 'Null'
        self.epithet = 'Null Hero'
        self.description = 'A mysterious Null Hero.'
        self.BVID = 0x0000

        #initialize basic unit attributes
        self.color = Color.RED
        self.weaponType = WeaponType.R_SWORD
        self.moveType = MoveType.INFANTRY
        self.tomeType = TomeType.NONE
        self.rarity = 5

        #initialize unit stats
        self._baseHP = 16
        self._baseAtk = 7
        self._baseSpd = 14
        self._baseDef = 5
        self._baseRes = 5
        self._baseTotal = (self._baseHP + self._baseAtk + self._baseSpd
                           + self._baseDef + self._baseRes)

        self._growthHP = 55
        self._growthAtk = 50
        self._growthSpd = 50
        self._growthDef = 50
        self._growthRes = 50
        self._growthTotal = (self._growthHP + self._growthAtk
                             + self._growthSpd + self._growthDef
                             + self._growthRes)

        self._maxHP = 38
        self._maxAtk = 29
        self._maxSpd = 36
        self._maxDef = 27
        self._maxRes = 27
        self._maxTotal = (self._maxHP + self._maxAtk + self._maxSpd
                          + self._maxDef + self._maxRes)

        self.summonerSupportLevel = 0

        #stat calc stuff
        self.isVeteran = False
        self.isTrainee = False
        self.isDancer = False
        self.isBrave = False
        self.generation = 1

        #legendary hero stuff
        self.isLegend = False
        self.legendElement = LegendElement.NONE
        self.legendBoost = LegendBoost.NONE

        #skills
        self.maxSpecialCooldown = None
        self.curSpecialCooldown = None

        self.skills = await SkillSet.create(heroName)

        self.equippedWeapon = None
        self.equippedAssist = None
        self.equippedSpecial = None
        self.equippedPassiveA = None
        self.equippedPassiveB = None
        self.equippedPassiveC = None
        self.equippedPassiveS = None

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

    @staticmethod
    async def lookup(name = 'null'):
        '''returns just the unit name'''
        return('null')

class CombatHero(Hero):
    '''Representation of a unit in combat'''

