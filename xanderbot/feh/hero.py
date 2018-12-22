import asyncio, sqlite3
from enum import Enum, unique
from feh.skill import Skill

@unique
class Color(Enum):
    '''Enum for each unit color'''
    NONE = 0
    RED = 1
    BLUE = 2
    GREEN = 3
    COLORLESS = 4

@unique
class UnitWeaponType(Enum):
    '''Enum for each weapon type'''
    NONE = 0
    R_SWORD = 1
    R_TOME = 2
    R_BREATH = 3
    B_LANCE = 4
    B_TOME = 5
    B_BREATH = 6
    G_AXE = 7
    G_TOME = 8
    G_BREATH = 9
    C_BOW = 10
    C_DAGGER = 11
    C_STAFF = 12
    C_BREATH = 13
    R_BOW = 14
    B_BOW = 15
    G_BOW = 16
    R_DAGGER = 17
    B_DAGGER = 18
    G_DAGGER = 19

@unique
class MoveType(Enum):
    '''Enum for each movement type'''
    INFANTRY = 1
    ARMOR = 2
    CAVALRY = 3
    FLIER = 4

@unique
class TomeType(Enum):
    '''Enum for tome elements, UNUSED'''
    NONE = 1
    FIRE = 2
    THUNDER = 3
    WIND = 4
    DARK = 5
    LIGHT = 6

@unique
class LegendElement(Enum):
    '''Enum for elements of Legendary Heroes'''
    NONE = 1
    FIRE = 2
    WATER = 3
    WIND = 4
    EARTH = 5
    LIGHT = 6
    DARK = 7
    ASTRA = 8
    ANIMA = 9

@unique
class Stat(Enum):
    '''Enum for each unit stat'''
    NONE = 1
    HP = 2
    ATK = 3
    SPD = 4
    DEF = 5
    RES = 6


class SkillSet(object):
    """Contains learnable skills of a hero"""
    @staticmethod
    def create():
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



    def __init__(self, name, epithet, color, weapon_type, move_type,
                 base_hp, base_atk, base_spd, base_def, base_res,
                 grow_hp, grow_atk, grow_spd, grow_def, grow_res,
                 max_hp, max_atk, max_spd, max_def, max_res,
                 is_legend = False, legend_element = LegendElement.NONE,
                 legend_boost = Stat.NONE, tome_type = TomeType.NONE,
                 description = 'No information available.', bvid = 0x0000,
                 art_portrait = '', art_attack = '', art_damaged = '',
                 art_special = '', artist = "Unknown", vo_en = 'Unknown',
                 vo_jp = 'Unknown', is_story = False, is_seasonal = False,
                 is_grail = False, is_veteran = False, is_trainee = False,
                 is_dancer = False, is_brave = False, is_sigurd=False,
                 generation = 1
                 ):
        '''
        Initializes an instance of a unit. The fields that aren't pre-defined
        are ones that a unit really wouldn't make much sense without.
        '''

        #initialize unit name
        self.name = name
        self.epithet = epithet
        self.description = description
        self.bvid = bvid

        #initialize basic unit attributes
        self.color = Color(color)
        self.weapon_type = UnitWeaponType(weapon_type)
        self.move_type = MoveType(move_type)
        #self.tome_type = TomeType(tome_type)
        self.rarity = 5
        self.level = 40
        self.merges = 0

        #skills
        self.skills = SkillSet.create()

        self.equipped_weapon    = None
        self.equipped_assist    = None
        self.equipped_special   = None
        self.equipped_passive_a = None
        self.equipped_passive_b = None
        self.equipped_passive_c = None
        self.equipped_passive_s = None

        #initialize unit stats, save intermediate steps to resume at any step
        #base stats == rarity:5 level:1 ivs:neutral merges:0
        #set by: initialization do not change
        #needed to calculate rarity
        self.base_hp  = base_hp
        self.base_atk = base_atk
        self.base_spd = base_spd
        self.base_def = base_def
        self.base_res = base_res
        self.base_total = (self.base_hp + self.base_atk + self.base_spd
                           + self.base_def + self.base_res)

        #iv stats == rarity:5 level:1 ivs: current merges:0
        #set by: update_ivs
        #needed to calculate merges
        self.iv_hp  = base_hp
        self.iv_atk = base_atk
        self.iv_spd = base_spd
        self.iv_def = base_def
        self.iv_res = base_res

        #merge stats == rarity:5 level:1 ivs:current merges:current
        #set by: update_merges
        #needed to calculate lv1 stats
        self.merge_hp  = base_hp
        self.merge_atk = base_atk
        self.merge_spd = base_spd
        self.merge_def = base_def
        self.merge_res = base_res

        #rarity mod == amount to subtract from stats due to rarity
        #separate this calc so that we can minimize the number of times its called
        self.rmod_hp  = 0
        self.rmod_atk = 0
        self.rmod_spd = 0
        self.rmod_def = 0
        self.rmod_res = 0

        #lv1 stats == rarity:current level:1 ivs:current merges:current
        #set by: update_rarity
        #displayed to user
        self.lv1_hp  = base_hp
        self.lv1_atk = base_atk
        self.lv1_spd = base_spd
        self.lv1_def = base_def
        self.lv1_res = base_res

        self.grow_hp  = grow_hp
        self.grow_atk = grow_atk
        self.grow_spd = grow_spd
        self.grow_def = grow_def
        self.grow_res = grow_res
        self.grow_total = (self.grow_hp + self.grow_atk + self.grow_spd
                           + self.grow_def + self.grow_res)
        
        #stats at lv40, including merges
        self.max_hp  = max_hp
        self.max_atk = max_atk
        self.max_spd = max_spd
        self.max_def = max_def
        self.max_res = max_res
        self.max_total = (self.max_hp + self.max_atk + self.max_spd
                          + self.max_def + self.max_res)

        #stats at any other lv
        self.curr_hp  = max_hp
        self.curr_atk = max_atk
        self.curr_spd = max_spd
        self.curr_def = max_def
        self.curr_res = max_res

        self.boon = Stat.NONE
        self.bane = Stat.NONE

        self.summoner_support_level = 0

        #legendary hero stuff
        self.is_legend = is_legend
        self.legend_element = LegendElement(legend_element)
        self.legend_boost = Stat(legend_boost)

        #other
        self.is_story = is_story
        self.is_seasonal = is_seasonal
        self.is_grail = is_grail

        #stat calc stuff
        self.is_veteran = is_veteran
        self.is_trainee = is_trainee
        self.is_dancer = is_dancer
        self.is_brave = is_brave
        self.is_sigurd = is_sigurd
        self.generation = generation

        #fluff
        self.art_portrait = art_portrait
        self.art_attack = art_attack
        self.art_special = art_special
        self.art_damaged = art_damaged
        self.artist = artist
        self.vo_en = vo_en
        self.vo_jp = vo_jp

        #bonus units
        self.is_arena_bonus = False
        self.is_aether_bonus = False
        self.is_aether_bonus_next = False
        self.is_tempest_bonus = False


    def get_boons_banes(self):
        boon_hp, boon_atk, boon_spd, boon_def, boon_res = 0, 0, 0, 0, 0
        five_star_boons = {5, 25, 45, 70}
        five_star_banes = {10, 30, 50, 75}
        four_star_boons = {10, 70}
        four_star_banes = {15, 75}
        #three_star_boons = {}
        #three_star_banes = {}
        #two_star_subboons = {20, 40, 70}
        #two_star_subbanes = {25, 45, 75}
        #one_star_subboons = {10, 25, 40, 55, 70}
        #one_star_subbanes = {15, 30, 45, 60, 75}
        
        if self.rarity == 5:
            if self.grow_hp  in five_star_boons: boon_hp  = 1
            elif self.grow_hp  in five_star_banes: boon_hp  = -1
            if self.grow_atk in five_star_boons: boon_atk = 1
            elif self.grow_atk in five_star_banes: boon_atk = -1
            if self.grow_spd in five_star_boons: boon_spd = 1
            elif self.grow_spd in five_star_banes: boon_spd = -1
            if self.grow_def in five_star_boons: boon_def = 1
            elif self.grow_def in five_star_banes: boon_def = -1
            if self.grow_res in five_star_boons: boon_res = 1
            elif self.grow_res in five_star_banes: boon_res = -1
        elif self.rarity == 4:
            if self.grow_hp  in four_star_boons: boon_hp  = 1
            elif self.grow_hp  in four_star_banes: boon_hp  = -1
            if self.grow_atk in four_star_boons: boon_atk = 1
            elif self.grow_atk in four_star_banes: boon_atk = -1
            if self.grow_spd in four_star_boons: boon_spd = 1
            elif self.grow_spd in four_star_banes: boon_spd = -1
            if self.grow_def in four_star_boons: boon_def = 1
            elif self.grow_def in four_star_banes: boon_def = -1
            if self.grow_res in four_star_boons: boon_res = 1
            elif self.grow_res in four_star_banes: boon_res = -1

        return boon_hp, boon_atk, boon_spd, boon_def, boon_res


    async def recalc_stats(self):
        '''
        updates max stats from lv1, growth, merges, and rarity
        '''
        self.lv1_hp  = self.merge_hp  + self.rmod_hp
        self.lv1_atk = self.merge_atk + self.rmod_atk
        self.lv1_spd = self.merge_spd + self.rmod_spd
        self.lv1_def = self.merge_def + self.rmod_def
        self.lv1_res = self.merge_res + self.rmod_res

        self.max_hp  = (
            self.lv1_hp
            + Hero.STATS_RARITY[self.rarity - 1][self.grow_hp //5]
            )
        self.max_atk = (
            self.lv1_atk
            + Hero.STATS_RARITY[self.rarity - 1][self.grow_atk//5]
            )
        self.max_spd = (
            self.lv1_spd
            + Hero.STATS_RARITY[self.rarity - 1][self.grow_spd//5]
            )
        self.max_def = (
            self.lv1_def
            + Hero.STATS_RARITY[self.rarity - 1][self.grow_def//5]
            )
        self.max_res = (
            self.lv1_res
            + Hero.STATS_RARITY[self.rarity - 1][self.grow_res//5]
            )

    def modify_rmod(self, stat_enum, amount):
        '''this is a convenience method to make update_rarity look cleaner'''
        #todo: investigate whether setattr() is faster (it probably isn't)
        if   stat_enum == Stat.HP:  self.rmod_hp  += amount
        elif stat_enum == Stat.ATK: self.rmod_atk += amount
        elif stat_enum == Stat.SPD: self.rmod_spd += amount
        elif stat_enum == Stat.DEF: self.rmod_def += amount
        elif stat_enum == Stat.RES: self.rmod_res += amount

    async def update_level(self, new_level):
        '''recalculates current stats based on level'''
        raise NotImplementedError("Get me those BVIDs and then we'll talk.")

    async def update_rarity(self, new_rarity):
        '''
        recalculates rarity mod from a rarity change
        no more relative calc since base stats saved all the time
        be sure to Hero.recalc_stats() afterwards!
        '''
        if new_rarity == self.rarity or new_rarity < 1 or new_rarity > 5: return
        self.rarity = new_rarity

        modify = 0
        if (new_rarity < 4):
            if new_rarity == 1: modify = -2
            else: modify = -1

        self.rmod_hp  = modify
        self.rmod_atk = modify
        self.rmod_spd = modify
        self.rmod_def = modify
        self.rmod_res = modify
        if new_rarity % 2 == 1: return

        stats = [
            (self.base_atk, 4, Stat.ATK),
            (self.base_spd, 3, Stat.SPD),
            (self.base_res, 1, Stat.RES),
            (self.base_def, 2, Stat.DEF),
            (            0, 0, Stat.HP )
            ]
        stats.sort(key=lambda sl: (sl[0], sl[1]))

        # modify smallest 3
        for i in range(3):
            self.modify_rmod(stats[i][2], -1)


    def modify_iv(self, iv, increase):
        '''another convenience method'''
        if iv == None: return
        elif increase:
            if iv == Stat.HP:
                self.iv_hp    += 1
                self.grow_hp  += 5
            elif iv == Stat.ATK:
                self.iv_atk   += 1
                self.grow_atk += 5
            elif iv == Stat.SPD:
                self.iv_spd   += 1
                self.grow_spd += 5
            elif iv == Stat.DEF:
                self.iv_def   += 1
                self.grow_def += 5
            elif iv == Stat.RES:
                self.iv_res   += 1
                self.grow_res += 5
        else:
            if iv == Stat.HP:
                self.iv_hp    -= 1
                self.grow_hp  -= 5
            elif iv == Stat.ATK:
                self.iv_atk   -= 1
                self.grow_atk -= 5
            elif iv == Stat.SPD:
                self.iv_spd   -= 1
                self.grow_spd -= 5
            elif iv == Stat.DEF:
                self.iv_def   -= 1
                self.grow_def -= 5
            elif iv == Stat.RES:
                self.iv_res   -= 1
                self.grow_res -= 5


    async def update_ivs(self, boon, bane):
        '''
        recalculates lv1 stats and growths from ivs
        note that this invalidates merge_stat
        '''
        if boon == bane and boon != Stat.NONE: return
        if self.boon != boon:
            self.modify_iv(self.boon, False)
            self.modify_iv(boon, True)
        if self.bane != bane:
            self.modify_iv(self.bane, True)
            self.modify_iv(bane, False)


    def modify_merge(self, stat_enum, amount):
        '''this is a convenience method to make update_merges look cleaner'''
        #todo: investigate whether setattr() is faster (it probably isn't)
        if   stat_enum == Stat.HP:  self.merge_hp  += amount
        elif stat_enum == Stat.ATK: self.merge_atk += amount
        elif stat_enum == Stat.SPD: self.merge_spd += amount
        elif stat_enum == Stat.DEF: self.merge_def += amount
        elif stat_enum == Stat.RES: self.merge_res += amount


    async def update_merges(self, new_merges):
        '''
        recalculates lv1 stats from merges
        we dont do this in a relative manner since its unlikely to be faster
        and updating ivs invalidate previous merge_stat
        be sure to Hero.recalc_stats() afterwards!
        '''
        if new_merges < 0 or new_merges > 10: return

        self.merges = new_merges
        modify = 0
        if new_merges >= 5:
            modify = 2
            new_merges -= 5
            if new_merges == 10: modify = 4

        self.merge_hp  = self.iv_hp  + modify
        self.merge_atk = self.iv_atk + modify
        self.merge_spd = self.iv_spd + modify
        self.merge_def = self.iv_def + modify
        self.merge_res = self.iv_res + modify
        if new_merges % 5 == 0: return

        stats = [
            (self.base_hp , 4, Stat.HP ),
            (self.base_atk, 3, Stat.ATK),
            (self.base_spd, 2, Stat.SPD),
            (self.base_def, 1, Stat.DEF),
            (self.base_res, 0, Stat.RES)
            ]
        stats.sort(key=lambda sl: (sl[0], sl[1]), reverse=True)

        for i in range(new_merges * 2):
            self.modify_merge(stats[i % 4][2], 1)


    async def update_stat_mods(
        self, *, boon = None, bane = None, merges = None, rarity = None):
        if boon and bane:
            await self.update_ivs(boon, bane)
        if merges != None:
            await self.update_merges(merges)
        if rarity:
            await self.update_rarity(rarity)
        if rarity or (boon and bane) or (merges != None):
            await self.recalc_stats()



class CombatHero(Hero):
    '''Representation of a unit in combat'''

