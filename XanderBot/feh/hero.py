import asyncio, sqlite3
from enum import Enum
from feh.skill import Skill

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
        self.passive_a = [None] * 6
        self.passive_b = [None] * 6
        self.passive_c = [None] * 6
        self.weapon_prf = None

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
        self.bvid = 0x0000

        #initialize basic unit attributes
        self.color = Color.RED
        self.weapon_type = WeaponType.R_SWORD
        self.move_type = MoveType.INFANTRY
        self.tome_type = TomeType.NONE
        self.rarity = 5

        #initialize unit stats
        self.base_hp = 16
        self.base_atk = 7
        self.base_spd = 14
        self.base_def = 5
        self.base_res = 5
        self.base_total = (self.base_hp + self.base_atk + self.base_spd
                           + self.base_def + self.base_res)

        self.growth_hp = 55
        self.growth_atk = 50
        self.growth_spd = 50
        self.growth_def = 50
        self.growth_res = 50
        self.growth_total = (self.growth_hp + self.growth_atk
                             + self.growth_spd + self.growth_def
                             + self.growth_res)

        self.max_hp = 38
        self.max_atk = 29
        self.max_spd = 36
        self.max_def = 27
        self.max_res = 27
        self.max_total = (self.max_hp + self.max_atk + self.max_spd
                          + self.max_def + self.max_res)

        self.summoner_support_level = 0

        #stat calc stuff
        self.is_veteran = False
        self.is_trainee = False
        self.is_dancer = False
        self.is_brave = False
        self.generation = 1

        #legendary hero stuff
        self.is_legend = False
        self.legend_element = LegendElement.NONE
        self.legend_boost = LegendBoost.NONE

        #skills
        self.max_special_cooldown = None

        self.skills = await SkillSet.create(heroName)

        self.equipped_weapon = None
        self.equipped_assist = None
        self.equipped_special = None
        self.equipped_passive_a = None
        self.equipped_passive_b = None
        self.equipped_passive_c = None
        self.equipped_passive_s = None

        #fluff
        self.art_portrait = ''
        self.art_attack = ''
        self.art_special = ''
        self.art_damaged = ''
        self.artist = ''
        self.vo_en = ''
        self.vo_jp = ''

        #bonus units
        self.is_arena_bonus = False
        self.is_aether_bonus = False
        self.is_aether_bonus_next = False
        self.is_tempest_bonus = False

        #other
        self.is_story = False
        self.is_seasonal = False
        self.is_grail = False

        return(self)

    @staticmethod
    async def lookup(name = 'null'):
        '''returns just the unit name'''
        return('null')

class CombatHero(Hero):
    '''Representation of a unit in combat'''

