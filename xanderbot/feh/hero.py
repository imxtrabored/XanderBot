from copy import copy
from enum import Enum, unique

@unique
class Color(Enum):
    '''Enum for each unit color'''
    NONE      = 0
    RED       = 1
    BLUE      = 2
    GREEN     = 3
    COLORLESS = 4

@unique
class UnitWeaponType(Enum):
    '''Enum for each weapon type'''
    NONE     = 0
    R_SWORD  = 1
    R_TOME   = 2
    R_BREATH = 3
    B_LANCE  = 4
    B_TOME   = 5
    B_BREATH = 6
    G_AXE    = 7
    G_TOME   = 8
    G_BREATH = 9
    C_BOW    = 10
    C_DAGGER = 11
    C_STAFF  = 12
    C_BREATH = 13
    R_BOW    = 14
    B_BOW    = 15
    G_BOW    = 16
    R_DAGGER = 17
    B_DAGGER = 18
    G_DAGGER = 19
    R_BEAST  = 20
    B_BEAST  = 21
    G_BEAST  = 22
    C_BEAST  = 23

@unique
class MoveType(Enum):
    '''Enum for each movement type'''
    INFANTRY = 1
    ARMOR    = 2
    CAVALRY  = 3
    FLIER    = 4

@unique
class TomeType(Enum):
    '''Enum for tome elements, UNUSED'''
    NONE    = 1
    FIRE    = 2
    THUNDER = 3
    WIND    = 4
    DARK    = 5
    LIGHT   = 6

@unique
class LegendElement(Enum):
    '''Enum for elements of Legendary Heroes'''
    NONE  = 1
    FIRE  = 2
    WATER = 3
    WIND  = 4
    EARTH = 5
    LIGHT = 6
    DARK  = 7
    ASTRA = 8
    ANIMA = 9

@unique
class LegendStat(Enum):
    '''Enum for each unit stat'''
    NONE = 1
    HP   = 2
    ATK  = 3
    SPD  = 4
    DEF  = 5
    RES  = 6

@unique
class Stat(Enum):
    '''Enum for each unit stat'''
    NONE = 1
    HP   = 2
    ATK  = 3
    SPD  = 4
    DEF  = 5
    RES  = 6


@unique
class Rarity(Enum):
    ONE   = 1
    TWO   = 2
    THREE = 3
    FOUR  = 4
    FIVE  = 5



class Hero(object):
    '''Representation of a unit in FEH'''

    #optimization
    __slots__ = (
        'id', 'identity', 'name', 'short_name', 'epithet', 'color',
        'weapon_type', 'move_type', 'rarity', 'level', 'merges',
        'weapon', 'assist', 'special', 'passive_a', 'passive_b',
        'passive_c', 'weapon_prf',
        'equipped_weapon', 'equipped_assist', 'equipped_special',
        'equipped_passive_a', 'equipped_passive_b', 'equipped_passive_c',
        'equipped_passive_s',
        'base_hp', 'base_atk', 'base_spd', 'base_def', 'base_res',
        'iv_hp', 'iv_atk', 'iv_spd', 'iv_def', 'iv_res',
        'merge_hp', 'merge_atk', 'merge_spd', 'merge_def', 'merge_res',
        'rmod_hp', 'rmod_atk', 'rmod_spd', 'rmod_def', 'rmod_res',
        'lv1_hp', 'lv1_atk', 'lv1_spd', 'lv1_def', 'lv1_res',
        'grow_hp', 'grow_atk', 'grow_spd', 'grow_def', 'grow_res',
        'max_hp', 'max_atk', 'max_spd', 'max_def', 'max_res',
        'curr_hp', 'curr_atk', 'curr_spd', 'curr_def', 'curr_res',
        'base_total', 'lv1_total', 'grow_total', 'max_total',
        'boon', 'bane', 'summoner_support_level',
        'is_legend', 'legend_element', 'legend_boost', 'tome_type',
        'description', 'bvid',
        'art_portrait', 'art_attack', 'art_damaged', 'art_special',
        'artist', 'vo_en', 'vo_jp', 'alt_base_id', 'alt_base', 'alt_list',
        'is_story', 'is_seasonal', 'is_grail', 'is_veteran', 'is_trainee',
        'is_dancer', 'is_brave', 'is_sigurd', 'generation',
        'is_arena_bonus', 'is_aether_bonus', 'is_aether_bonus_next',
        'is_tempest_bonus', 'newmerges'
    )

    # we could calculate this easily, but this is faster anyways
    STATS_RARITY = (
        (),
        (0, 1, 3, 4, 6, 8, 9, 11, 13, 14,
         16, 18, 19, 21, 23, 24, 26, 28),
        (0, 1, 3, 5, 7, 8, 10, 12, 14, 15,
         17, 19, 21, 23, 25, 26, 28, 30),
        (0, 1, 3, 5, 7, 9, 11, 13, 15, 17,
         19, 21, 23, 25, 27, 29, 31, 33),
        (0, 1, 3, 6, 8, 10, 12, 14, 16, 18,
         20, 22, 24, 26, 28, 31, 33, 35),
        (0, 1, 4, 6, 8, 10, 13, 15, 17, 19,
         22, 24, 26, 28, 30, 33, 35, 37),
    )



    def __init__(
            self, id, identity, name, short_name, epithet, color,
            weapon_type, move_type,
            base_hp, base_atk, base_spd, base_def, base_res,
            grow_hp, grow_atk, grow_spd, grow_def, grow_res,
            max_hp, max_atk, max_spd, max_def, max_res,
            is_legend = False, legend_element = LegendElement.NONE,
            legend_boost = LegendStat.NONE, tome_type = TomeType.NONE,
            description = 'No information available.', bvid = 0x0000,
            artist = "Unknown", vo_en = 'Unknown', vo_jp = 'Unknown',
            alt_base_id = None,
            is_story = False, is_seasonal = False, is_grail = False,
            is_veteran = False, is_trainee = False, is_dancer = False,
            is_brave = False, is_sigurd = False,
            generation = 1
    ):
        '''
        Initializes an instance of a unit. The fields that aren't pre-defined
        are ones that a unit really wouldn't make much sense without.
        '''

        #initialize unit name
        self.id = id
        self.identity = identity
        self.name = name
        self.short_name = short_name
        self.epithet = epithet
        self.description = description
        self.bvid = bvid

        #initialize basic unit attributes
        self.color = Color(color)
        self.weapon_type = UnitWeaponType(weapon_type)
        self.move_type = MoveType(move_type)
        self.tome_type = TomeType(tome_type)
        self.rarity = 5
        self.level = 40
        self.merges = 0

        #skills
        self.weapon = []
        self.assist = []
        self.special = []
        self.passive_a = []
        self.passive_b = []
        self.passive_c = []
        self.weapon_prf = None

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
        self.merge_hp  = 0
        self.merge_atk = 0
        self.merge_spd = 0
        self.merge_def = 0
        self.merge_res = 0

        #rarity mod == amount to subtract from stats due to rarity
        #separate this calc so that we can minimize number of times its called
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
        self.lv1_total = (self.lv1_hp + self.lv1_atk + self.lv1_spd
                          + self.lv1_def + self.lv1_res)

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
        self.legend_boost = LegendStat(legend_boost)

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
        self.art_portrait = ''
        self.art_attack = ''
        self.art_special = ''
        self.art_damaged = ''
        self.artist = artist
        self.vo_en = vo_en
        self.vo_jp = vo_jp

        self.alt_base_id = alt_base_id
        self_alt_base = None
        self.alt_list = []

        #bonus units
        self.is_arena_bonus = False
        self.is_aether_bonus = False
        self.is_aether_bonus_next = False
        self.is_tempest_bonus = False

        self.newmerges = False



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
        if self.boon != Stat.NONE or self.bane != Stat.NONE:
            return boon_hp, boon_atk, boon_spd, boon_def, boon_res

        if self.rarity == 5:
            if   self.grow_hp  in five_star_boons: boon_hp  =  1
            elif self.grow_hp  in five_star_banes: boon_hp  = -1
            if   self.grow_atk in five_star_boons: boon_atk =  1
            elif self.grow_atk in five_star_banes: boon_atk = -1
            if   self.grow_spd in five_star_boons: boon_spd =  1
            elif self.grow_spd in five_star_banes: boon_spd = -1
            if   self.grow_def in five_star_boons: boon_def =  1
            elif self.grow_def in five_star_banes: boon_def = -1
            if   self.grow_res in five_star_boons: boon_res =  1
            elif self.grow_res in five_star_banes: boon_res = -1
        elif self.rarity == 4:
            if   self.grow_hp  in four_star_boons: boon_hp  =  1
            elif self.grow_hp  in four_star_banes: boon_hp  = -1
            if   self.grow_atk in four_star_boons: boon_atk =  1
            elif self.grow_atk in four_star_banes: boon_atk = -1
            if   self.grow_spd in four_star_boons: boon_spd =  1
            elif self.grow_spd in four_star_banes: boon_spd = -1
            if   self.grow_def in four_star_boons: boon_def =  1
            elif self.grow_def in four_star_banes: boon_def = -1
            if   self.grow_res in four_star_boons: boon_res =  1
            elif self.grow_res in four_star_banes: boon_res = -1

        return boon_hp, boon_atk, boon_spd, boon_def, boon_res



    def recalc_stats(self):
        '''
        updates max stats from lv1, growth, merges, and rarity
        '''
        self.lv1_hp  = self.iv_hp  + self.merge_hp  + self.rmod_hp
        self.lv1_atk = self.iv_atk + self.merge_atk + self.rmod_atk
        self.lv1_spd = self.iv_spd + self.merge_spd + self.rmod_spd
        self.lv1_def = self.iv_def + self.merge_def + self.rmod_def
        self.lv1_res = self.iv_res + self.merge_res + self.rmod_res

        self.max_hp  = (
            self.lv1_hp
            + Hero.STATS_RARITY[self.rarity][self.grow_hp // 5]
        )
        self.max_atk = (
            self.lv1_atk
            + Hero.STATS_RARITY[self.rarity][self.grow_atk// 5]
        )
        self.max_spd = (
            self.lv1_spd
            + Hero.STATS_RARITY[self.rarity][self.grow_spd// 5]
        )
        self.max_def = (
            self.lv1_def
            + Hero.STATS_RARITY[self.rarity][self.grow_def// 5]
        )
        self.max_res = (
            self.lv1_res
            + Hero.STATS_RARITY[self.rarity][self.grow_res// 5]
        )
        self.max_total = (self.max_hp + self.max_atk + self.max_spd
                          + self.max_def + self.max_res)



    def modify_rmod(self, stat_enum, amount):
        '''this is a convenience method to make update_rarity look cleaner'''
        #todo: investigate whether setattr() is faster (it probably isn't)
        if   stat_enum == Stat.HP:  self.rmod_hp  += amount
        elif stat_enum == Stat.ATK: self.rmod_atk += amount
        elif stat_enum == Stat.SPD: self.rmod_spd += amount
        elif stat_enum == Stat.DEF: self.rmod_def += amount
        elif stat_enum == Stat.RES: self.rmod_res += amount



    def update_level(self, new_level):
        '''recalculates current stats based on level'''
        raise NotImplementedError("Get me those BVIDs and then we'll talk.")



    def update_rarity(self, new_rarity):
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
            (            0, 0, Stat.HP ),
        ]
        stats.sort(key=lambda sl: (sl[0], sl[1]))

        # modify smallest 3
        for i in range(3):
            self.modify_rmod(stats[i][2], -1)



    def modify_iv(self, iv, increase):
        '''another convenience method'''
        if iv is None: return
        if increase:
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



    def update_ivs(self, boon, bane):
        '''
        recalculates lv1 stats and growths from ivs
        note that this invalidates merge_stat
        '''
        if boon == bane and boon != Stat.NONE: return
        if self.boon != boon:
            self.modify_iv(self.boon, False)
            self.modify_iv(boon, True)
            self.boon = boon
        if self.bane != bane:
            self.modify_iv(self.bane, True)
            self.modify_iv(bane, False)
            self.bane = bane



    def modify_merge(self, stat_enum, amount):
        '''this is a convenience method to make update_merges look cleaner'''
        #todo: investigate whether setattr() is faster (it probably isn't)
        if   stat_enum == Stat.HP:  self.merge_hp  += amount
        elif stat_enum == Stat.ATK: self.merge_atk += amount
        elif stat_enum == Stat.SPD: self.merge_spd += amount
        elif stat_enum == Stat.DEF: self.merge_def += amount
        elif stat_enum == Stat.RES: self.merge_res += amount



    def update_merges(self, new_merges):
        '''
        recalculates lv1 stats from merges
        we do this in a relative manner since its unlikely to be faster
        and updating ivs invalidate previous merge_stat
        be sure to Hero.recalc_stats() afterwards!
        '''
        if new_merges < 0 or new_merges > 10: return

        self.merges = new_merges
        modify = 0

        if new_merges == 0:
            self.merge_hp  = 0
            self.merge_atk = 0
            self.merge_spd = 0
            self.merge_def = 0
            self.merge_res = 0
            return
        if new_merges == 10:
            modify = 4
            new_merges = 0
        elif new_merges >= 5:
            modify = 2
            new_merges -= 5

        self.merge_hp  = modify
        self.merge_atk = modify
        self.merge_spd = modify
        self.merge_def = modify
        self.merge_res = modify

        stats = [
            (self.iv_hp , 4, Stat.HP ),
            (self.iv_atk, 3, Stat.ATK),
            (self.iv_spd, 2, Stat.SPD),
            (self.iv_def, 1, Stat.DEF),
            (self.iv_res, 0, Stat.RES),
        ]
        stats.sort(key = lambda sl: (sl[0], sl[1]), reverse = True)

        if self.newmerges:
            if self.bane == Stat.NONE:
                for i in range(3):
                    self.modify_merge(stats[i][2], 1)
            elif self.bane == Stat.HP:
                self.modify_merge(
                    Stat.HP,
                    Hero.STATS_RARITY[self.rarity][(self.grow_hp + 5) // 5]
                    - Hero.STATS_RARITY[self.rarity][self.grow_hp // 5]
                    + 1
                )
            elif self.bane == Stat.ATK:
                self.modify_merge(
                    Stat.ATK,
                    Hero.STATS_RARITY[self.rarity][(self.grow_atk + 5) // 5]
                    - Hero.STATS_RARITY[self.rarity][self.grow_atk // 5]
                    + 1
                )
            elif self.bane == Stat.SPD:
                self.modify_merge(
                    Stat.SPD,
                    Hero.STATS_RARITY[self.rarity][(self.grow_spd + 5) // 5]
                    - Hero.STATS_RARITY[self.rarity][self.grow_spd // 5]
                    + 1
                )
            elif self.bane == Stat.DEF:
                self.modify_merge(
                    Stat.DEF,
                    Hero.STATS_RARITY[self.rarity][(self.grow_def + 5) // 5]
                    - Hero.STATS_RARITY[self.rarity][self.grow_def // 5]
                    + 1
                )
            elif self.bane == Stat.RES:
                self.modify_merge(
                    Stat.RES,
                    Hero.STATS_RARITY[self.rarity][(self.grow_res + 5) // 5]
                    - Hero.STATS_RARITY[self.rarity][self.grow_res // 5]
                    + 1
                )

        for i in range(new_merges * 2):
            self.modify_merge(stats[i % 5][2], 1)



    def update_stat_mods(self, *, boon = None, bane = None, merges = None,
                         rarity = None):
        if ((boon and bane)
            and ((boon != Stat.NONE and bane != Stat.NONE)
                 or (boon == bane))):
            self.update_ivs(boon, bane)
            update_boons = True
        else: update_boons = False
        if rarity:
            self.update_rarity(rarity)
        if merges is not None:
            self.update_merges(merges)
        if rarity or update_boons or merges is not None:
            self.recalc_stats()



    def get_merge_table(self):
        '''
        this is slow but kind of annoyingly nested so i couldnt really come up
        with the quick one liner solution, maybe optimize?
        '''
        stats = [
            (self.iv_hp , 4, Stat.HP , 0),
            (self.iv_atk, 3, Stat.ATK, 1),
            (self.iv_spd, 2, Stat.SPD, 2),
            (self.iv_def, 1, Stat.DEF, 3),
            (self.iv_res, 0, Stat.RES, 4),
        ]
        stats.sort(key = lambda sl: (sl[0], sl[1]), reverse = True)
        merge_table = [[0, 0, 0, 0, 0]]

        if   self.bane == Stat.NONE:
            for i in range(3):
                merge_table[0][stats[i][3]] = 1
        elif self.bane == Stat.HP:
            merge_table[0][0] = (
                Hero.STATS_RARITY[self.rarity][(self.grow_hp  + 5) // 5]
                - Hero.STATS_RARITY[self.rarity][self.grow_hp  // 5]
                + 1
            )
        elif self.bane == Stat.ATK:
            merge_table[0][1] = (
                Hero.STATS_RARITY[self.rarity][(self.grow_atk + 5) // 5]
                - Hero.STATS_RARITY[self.rarity][self.grow_atk // 5]
                + 1
            )
        elif self.bane == Stat.SPD:
            merge_table[0][2] = (
                Hero.STATS_RARITY[self.rarity][(self.grow_spd + 5) // 5]
                - Hero.STATS_RARITY[self.rarity][self.grow_spd // 5]
                + 1
            )
        elif self.bane == Stat.DEF:
            merge_table[0][3] = (
                Hero.STATS_RARITY[self.rarity][(self.grow_def + 5) // 5]
                - Hero.STATS_RARITY[self.rarity][self.grow_def // 5]
                + 1
            )
        elif self.bane == Stat.RES:
            merge_table[0][4] = (
                Hero.STATS_RARITY[self.rarity][(self.grow_res + 5) // 5]
                - Hero.STATS_RARITY[self.rarity][self.grow_res // 5]
                + 1
            )

        for i in range(2):
            merge_table[0][stats[i][3]] += 1
        for i in range(9):
            merge_row = copy(merge_table[i])
            merge_row[stats[(2 * i + 2) % 5][3]] += 1
            merge_row[stats[(2 * i + 3) % 5][3]] += 1
            merge_table.append(merge_row)
        return merge_table



    def link(self, unit_lib):
        if self.alt_base_id:
            self.alt_base = unit_lib.get_rhero_by_id(self.alt_base_id)
            self.alt_base.alt_list.append(self)



    def sanity_check(self):
        if   self.rarity == 5: stat_total = 47
        elif self.rarity == 4: stat_total = 44
        elif self.rarity == 3: stat_total = 42
        elif self.rarity == 2: stat_total = 39
        elif self.rarity == 1: stat_total = 37
        else: print(f'{self.identity} invalid rarity: {self.rarity}')

        if self.generation != 1 and self.generation != 2:
            print(f'{self.identity} invalid generation: {self.generation}')

        growth_rate = 255

        ranged = self.weapon_type in (
            UnitWeaponType.R_TOME  ,
            UnitWeaponType.B_TOME  ,
            UnitWeaponType.G_TOME  ,
            UnitWeaponType.C_BOW   ,
            UnitWeaponType.C_DAGGER,
            UnitWeaponType.C_STAFF ,
            UnitWeaponType.R_BOW   ,
            UnitWeaponType.B_BOW   ,
            UnitWeaponType.G_BOW   ,
            UnitWeaponType.R_DAGGER,
            UnitWeaponType.B_DAGGER,
            UnitWeaponType.G_DAGGER,
        )

        if self.is_trainee:
            stat_total -= 8
            growth_rate += 30
        if self.is_veteran:
            stat_total += 8
            growth_rate -= 30
        if self.is_dancer:
            stat_total -= 8
        if ranged:
            stat_total -= 3
            growth_rate -= 15
        if self.move_type == MoveType.ARMOR:
            stat_total += 7
            growth_rate += 10
        if self.move_type == MoveType.CAVALRY:
            stat_total -= 1
            growth_rate -= 5
        if self.is_brave:
            growth_rate += 10
        if self.generation == 2 and not self.is_dancer:
            stat_total += 1
            growth_rate += 10
            if ranged and self.move_type != MoveType.ARMOR:
                growth_rate -= 5
            if self.move_type == MoveType.CAVALRY:
                stat_total -= 1
                growth_rate -= 5
            if self.move_type == MoveType.FLIER:
                stat_total -= 1
            if self.is_sigurd:
                growth_rate += 5

        if self.base_total != stat_total:
            print(f'{self.identity} failed stat total: '
                  f'expected {stat_total} but got {self.base_total}')
        if self.grow_total != growth_rate:
            print(f'{self.identity} failed growth rate: '
                  f'expected {growth_rate} but got {self.grow_total}')

        max_hp  = (self.base_hp
                   + Hero.STATS_RARITY[self.rarity][self.grow_hp  // 5])
        if max_hp  != self.max_hp :
            print(f'{self.identity} failed max hp: '
                  f'expected {max_hp } but got {self.max_hp }')
        max_atk = (self.base_atk
                   + Hero.STATS_RARITY[self.rarity][self.grow_atk // 5])
        if max_atk != self.max_atk:
            print(f'{self.identity} failed max atk: '
                  f'expected {max_atk} but got {self.max_atk}')
        max_spd  = (self.base_spd
                    + Hero.STATS_RARITY[self.rarity][self.grow_spd // 5])
        if max_spd != self.max_spd:
            print(f'{self.identity} failed max spd: '
                  f'expected {max_spd} but got {self.max_spd}')
        max_def = (self.base_def
                   + Hero.STATS_RARITY[self.rarity][self.grow_def // 5])
        if max_def != self.max_def:
            print(f'{self.identity} failed max def: '
                  f'expected {max_def} but got {self.max_def}')
        max_res = (self.base_res
                   + Hero.STATS_RARITY[self.rarity][self.grow_res // 5])
        if max_res != self.max_res:
            print(f'{self.identity} failed max res: '
                  f'expected {max_res} but got {self.max_res}')



class CombatHero(Hero):
    '''Representation of a unit in combat'''
    pass
