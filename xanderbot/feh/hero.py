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

class LegendElement(Enum):
    '''Enum for elements of Legendary Heroes'''
    NONE = 0
    FIRE = 1
    WATER = 2
    WIND = 3
    EARTH = 4

class Stat(Enum):
    '''Enum for each unit stat'''
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

        self.weapon = []
        self.assist = []
        self.special = []
        self.passive_a = []
        self.passive_b = []
        self.passive_c = []
        self.weapon_prf = None

        return self

class Hero(object):
    '''Representation of a unit in FEH'''

    # we could calculate this easily, but this is faster anyways
    STATS_RARITY = (
        (0, 1, 3, 4, 6, 8, 9, 11, 13, 14,
         16, 18, 19, 21, 23, 24, 26, 28),
        (0, 1, 3, 5, 7, 8, 10, 12, 14, 15,
         17, 19, 21, 23, 25, 26, 28, 30),
        (0, 1, 3, 5, 7, 9, 11, 13, 15, 17,
         19, 21, 23, 25, 27, 29, 31, 33),
        (0, 1, 3, 6, 8, 10, 12, 14, 16, 18,
         20, 22, 24, 26, 28, 31, 33, 35),
        (0, 1, 4, 6, 8, 10, 13, 15, 17, 19,
         22, 24, 26, 28, 30, 33, 35, 37)
        )

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

        self.boon = Stat.NONE
        self.bane = Stat.NONE

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
        self.legend_boost = Stat.NONE

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

        #await self.sort_stats()

        return(self)

    @staticmethod
    async def lookup(name = 'null'):
        '''returns just the unit name'''
        return('null')

    async def recalc_stats(self):
        '''updates max stats from base, growth, and rarity'''
        self.max_hp  = (
            self.base_hp
            + Hero.STATS_RARITY[self.rarity + 1][self.growth_hp //5]
            )
        self.max_atk = (
            self.base_atk
            + Hero.STATS_RARITY[self.rarity + 1][self.growth_atk//5]
            )
        self.max_spd = (
            self.base_spd
            + Hero.STATS_RARITY[self.rarity + 1][self.growth_spd//5]
            )
        self.max_def = (
            self.base_def
            + Hero.STATS_RARITY[self.rarity + 1][self.growth_def//5]
            )
        self.max_res = (
            self.base_res
            + Hero.STATS_RARITY[self.rarity + 1][self.growth_res//5]
            )

    def modify_base_stat(self, stat_enum, amount):
        '''this is a convenience method to make update_rarity look cleaner'''
        if   stat_enum == Stat.HP:  self.base_hp  += amount
        elif stat_enum == Stat.ATK: self.base_atk += amount
        elif stat_enum == Stat.SPD: self.base_spd += amount
        elif stat_enum == Stat.DEF: self.base_def += amount
        elif stat_enum == Stat.RES: self.base_res += amount

    async def update_rarity(self, new_rarity):
        '''recalculates base stats from a rarity change'''
        if  self.rarity == new_rarity or new_rarity < 1 or new_rarity > 5: return

        # microoptimization here
        self.rarity - new_rarity == rarity_diff
        if (rarity_diff > 1 or rarity_diff < 1):
            if (rarity_diff) % 2 == 0:
                if   rarity_diff ==  2: modify = -1
                elif rarity_diff ==  4: modify = -2
                elif rarity_diff == -2: modify =  1
                elif rarity_diff == -4: modify =  2
                self.rarity = new_rarity

            else:
                # rarity diff must be 3 or 5
                if   rarity_diff ==  3:
                    modify = -1
                    self.rarity -= 2
                elif rarity_diff ==  5:
                    modify = -2
                    self.rarity -= 4
                elif rarity_diff == -3:
                    modify =  1
                    self.rarity += 2
                elif rarity_diff == -5:
                    modify =  2
                    self.rarity += 4

            self.base_hp  += modify
            self.base_atk += modify
            self.base_spd += modify
            self.base_def += modify
            self.base_res += modify
            if (rarity_diff) % 2 == 0: return

        stats = [
            (self.base_atk, 4, Stat.ATK),
            (self.base_spd, 3, Stat.SPD),
            (self.base_res, 1, Stat.RES),
            (self.base_def, 2, Stat.DEF),
            (            0, 0, Stat.HP )
            ]
        stats.sort(key=lambda sl: (sl[0], sl[1]))

        if rarity_diff > 0:
            if self.rarity % 2 == 1:
                # modify smallest 3
                self.modify_base_stat(stats[i][2], -1)
            else:
                for i in range(3, 5):
                    # modify largest two
                    self.modify_base_stat(stats[i][2], -1)
            self.rarity
        else:
            if self.rarity % 2 == 1:
                # modify largest two
                self.modify_base_stat(stats[i][2], 1)
            else:
                # modify smallest 3
                self.modify_base_stat(stats[i][2], 1)

        self.rarity = new_rarity
                


class CombatHero(Hero):
    '''Representation of a unit in combat'''


