from copy import copy
from enum import Enum, unique


class OrderedEnum(Enum):
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


@unique
class UnitColor(OrderedEnum):
    '''Enum for each unit color'''
    NONE      = 0
    RED       = 1
    BLUE      = 2
    GREEN     = 3
    COLORLESS = 4

@unique
class UnitWeaponType(OrderedEnum):
    '''Enum for each weapon type'''
    NONE     = 0
    R_SWORD  = 1
    B_LANCE  = 2
    G_AXE    = 3
    R_BOW    = 4
    B_BOW    = 5
    G_BOW    = 6
    C_BOW    = 7
    R_DAGGER = 8
    B_DAGGER = 9
    G_DAGGER = 10
    C_DAGGER = 11
    R_TOME   = 12
    B_TOME   = 13
    G_TOME   = 14
    C_STAFF  = 15
    R_BREATH = 16
    B_BREATH = 17
    G_BREATH = 18
    C_BREATH = 19
    R_BEAST  = 20
    B_BEAST  = 21
    G_BEAST  = 22
    C_BEAST  = 23

@unique
class MoveType(OrderedEnum):
    '''Enum for each movement type'''
    INFANTRY = 1
    ARMOR    = 2
    CAVALRY  = 3
    FLIER    = 4

@unique
class TomeType(Enum):
    '''Enum for tome elements, UNUSED'''
    NONE    = None
    FIRE    = 1
    THUNDER = 2
    WIND    = 3
    DARK    = 4
    LIGHT   = 5

@unique
class LegendElement(Enum):
    '''Enum for elements of Legendary Heroes'''
    NONE  = None
    FIRE  = 1
    WATER = 2
    WIND  = 3
    EARTH = 4
    LIGHT = 5
    DARK  = 6
    ASTRA = 7
    ANIMA = 8

@unique
class LegendStat(Enum):
    '''Enum for each unit stat'''
    NONE = None
    HP   = 1
    ATK  = 2
    SPD  = 3
    DEF  = 4
    RES  = 5
    DUEL = 6

@unique
class Stat(Enum):
    '''Enum for each unit stat'''
    NONE = (1, 'None', 'None', '', '', set())
    HP   = (2, 'HP', 'Hit Points', 'hero.max_hp', 'hero.final_hp',
            {'hp', 'hitpoint', 'hitpoints', 'h',})
    ATK  = (3, 'Atk', 'Attack', 'hero.max_atk', 'hero.final_atk',
            {'atk', 'attack', 'a',})
    SPD  = (4, 'Spd', 'Speed', 'hero.max_spd', 'hero.final_spd',
            {'spd', 'speed', 's',})
    DEF  = (5, 'Def', 'Defense', 'hero.max_def', 'hero.final_def',
            {'def', 'defense', 'defence', 'd',})
    RES  = (6, 'Res', 'Resistance', 'hero.max_res', 'hero.final_res',
            {'res', 'resistance', 'r',})

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _, short, long, db_col, hero_final, aliases):
        self.short = short
        self.long = long
        self.db_col = db_col
        self.hero_final = hero_final
        self.aliases = aliases

    @classmethod
    def get_by_name(cls, name):
        for stat in cls:
            if name in stat.aliases:
                return stat
        return None

@unique
class Rarity(Enum):
    ONE   = 1
    TWO   = 2
    THREE = 3
    FOUR  = 4
    FIVE  = 5
    STONE = 11
    DEW   = 12

@unique
class SummonerSupport(Enum):
    NONE = 0
    C = 1
    B = 2
    A = 3
    S = 4

@unique
class SkillType(Enum):
    '''Enum for each skill type'''
    NONE           = 0
    WEAPON         = 1
    ASSIST         = 2
    SPECIAL        = 3
    PASSIVE_A      = 4
    PASSIVE_B      = 5
    PASSIVE_C      = 6
    PASSIVE_SEAL   = 7
    WEAPON_REFINED = 8
    REFINE         = 9


class EquipList(object):

    __slots__ = (
        'weapon', 'assist', 'special', 'passive_a', 'passive_b', 'passive_c',
        'passive_s'
    )

    def __init__(self):
        self.weapon = None
        self.assist = None
        self.special = None
        self.passive_a = None
        self.passive_b = None
        self.passive_c = None
        self.passive_s = None

    def __iter__(self):
        if self.weapon:
            yield self.weapon
        if self.assist:
            yield self.assist
        if self.special:
            yield self.special
        if self.passive_a:
            yield self.passive_a
        if self.passive_b:
            yield self.passive_b
        if self.passive_c:
            yield self.passive_c
        if self.passive_s:
            yield self.passive_s
        return


class Hero(object):
    '''Representation of a unit in FEH'''

    #optimization
    __slots__ = (
        'index', 'name', 'custom_name', 'short_name', 'epithet', 'color',
        'weapon_type', 'move_type', 'rarity', 'level', 'merges',
        'flowers', 'merge_boon', 'merge_bane', 'merge_order',
        'weapon', 'assist', 'special', 'passive_a', 'passive_b',
        'passive_c', 'weapon_prf', 'equipped',
        'base_hp', 'base_atk', 'base_spd', 'base_def', 'base_res',
        'iv_hp', 'iv_atk', 'iv_spd', 'iv_def', 'iv_res',
        'merge_hp', 'merge_atk', 'merge_spd', 'merge_def', 'merge_res',
        'df_hp', 'df_atk', 'df_spd', 'df_def', 'df_res',
        'rmod_hp', 'rmod_atk', 'rmod_spd', 'rmod_def', 'rmod_res',
        'lv1_hp', 'lv1_atk', 'lv1_spd', 'lv1_def', 'lv1_res',
        'grow_hp', 'grow_atk', 'grow_spd', 'grow_def', 'grow_res',
        'max_hp', 'max_atk', 'max_spd', 'max_def', 'max_res',
        'curr_hp', 'curr_atk', 'curr_spd', 'curr_def', 'curr_res',
        'base_total', 'lv1_total', 'grow_total', 'max_total',
        'boon', 'bane', 'summ_support',
        'is_legend', 'legend_element', 'legend_boost', 'tome_type',
        'description', 'bvid',
        'artist', 'vo_en', 'vo_jp', 'alt_base_id', 'alt_base', 'alt_list',
        'is_story', 'is_seasonal', 'is_grail', 'is_veteran', 'is_trainee',
        'is_dancer', 'is_brave', 'is_sigurd', 'is_enemy', 'generation',
        'is_arena_bonus', 'is_aether_bonus', 'is_aether_bonus_next',
        'is_tempest_bonus', 'sort_dummy', 'sort_values',
        'p_hero_id', 'p_custom', 'p_atk', 'p_spd', 'p_def', 'p_res',
    )

    # we could calculate this easily, but this is faster anyways
    # first element of row 2 is 50% growths
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
            self, index, name, short_name, epithet, color,
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
            is_brave = False, is_sigurd = False, is_enemy = 0,
            generation = 1
    ):
        '''
        Initializes an instance of a unit. The fields that aren't pre-defined
        are ones that a unit really wouldn't make much sense without.
        '''

        #initialize unit name
        self.index = index
        self.name = name
        self.custom_name = None
        self.short_name = short_name
        self.epithet = epithet
        self.description = description
        self.bvid = bvid

        #initialize basic unit attributes
        self.color = UnitColor(color)
        self.weapon_type = UnitWeaponType(weapon_type)
        self.move_type = MoveType(move_type)
        self.tome_type = TomeType(tome_type)
        self.rarity = 5
        self.level = 40
        self.merges = 0
        self.flowers = 0

        #skills
        self.weapon = []
        self.assist = []
        self.special = []
        self.passive_a = []
        self.passive_b = []
        self.passive_c = []
        self.weapon_prf = None
        self.equipped = EquipList()

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

        self.df_hp  = 0
        self.df_atk = 0
        self.df_spd = 0
        self.df_def = 0
        self.df_res = 0

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
        self.reset_merge_order()

        self.summ_support = 0

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
        self.is_enemy = is_enemy
        self.generation = generation

        #fluff
        self.artist = artist
        self.vo_en = vo_en
        self.vo_jp = vo_jp

        self.alt_base_id = alt_base_id
        self.alt_base = None
        self.alt_list = []

        #bonus units
        self.is_arena_bonus = False
        self.is_aether_bonus = False
        self.is_aether_bonus_next = False
        self.is_tempest_bonus = False

        self.p_hero_id = None
        self.p_custom = None
        self.p_atk = 0
        self.p_spd = 0
        self.p_def = 0
        self.p_res = 0

        self.sort_dummy = None
        self.sort_values = None

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.index == other.index
        return NotImplemented

    @property
    def start_hp(self):
        return sum([skill.bonus_hp for skill in self.equipped], self.lv1_hp)
    @property
    def start_atk(self):
        return sum([skill.bonus_atk for skill in self.equipped], self.lv1_atk)
    @property
    def start_spd(self):
        return sum([skill.bonus_spd for skill in self.equipped], self.lv1_spd)
    @property
    def start_def(self):
        return sum([skill.bonus_def for skill in self.equipped], self.lv1_def)
    @property
    def start_res(self):
        return sum([skill.bonus_res for skill in self.equipped], self.lv1_res)
    @property
    def start_total(self):
        return sum((self.start_hp, self.start_atk, self.start_spd,
                    self.start_def, self.start_res))
    @property
    def final_hp(self):
        return sum([skill.bonus_hp  for skill in self.equipped], self.max_hp)
    @property
    def final_atk(self):
        return sum([skill.bonus_atk for skill in self.equipped], self.max_atk)
    @property
    def final_spd(self):
        return sum([skill.bonus_spd for skill in self.equipped], self.max_spd)
    @property
    def final_def(self):
        return sum([skill.bonus_def for skill in self.equipped], self.max_def)
    @property
    def final_res(self):
        return sum([skill.bonus_res for skill in self.equipped], self.max_res)
    @property
    def final_total(self):
        return sum((self.final_hp, self.final_atk, self.final_spd,
                    self.final_def, self.final_res))

    @property
    def bst_score(self):
        max_hp  = (self.iv_hp  + self.rmod_hp
               + Hero.STATS_RARITY[self.rarity][self.grow_hp // 5])
        max_atk = (self.iv_atk + self.rmod_atk
               + Hero.STATS_RARITY[self.rarity][self.grow_atk // 5])
        max_spd = (self.iv_spd + self.rmod_spd
               + Hero.STATS_RARITY[self.rarity][self.grow_spd // 5])
        max_def = (self.iv_def + self.rmod_def
               + Hero.STATS_RARITY[self.rarity][self.grow_def // 5])
        max_res = (self.iv_res + self.rmod_res
               + Hero.STATS_RARITY[self.rarity][self.grow_res // 5])
        bonus = 0
        if self.merges > 0:
            if self.bane == Stat.NONE:
                bonus = 3
            elif self.bane == Stat.HP:
                max_hp  += (
                    Hero.STATS_RARITY[self.rarity][(self.grow_hp + 5) // 5]
                    - Hero.STATS_RARITY[self.rarity][self.grow_hp // 5] + 1
                )
            elif self.bane == Stat.ATK:
                max_atk += (
                    Hero.STATS_RARITY[self.rarity][(self.grow_atk + 5) // 5]
                    - Hero.STATS_RARITY[self.rarity][self.grow_atk // 5] + 1
                )
            elif self.bane == Stat.SPD:
                max_spd += (
                    Hero.STATS_RARITY[self.rarity][(self.grow_spd + 5) // 5]
                    - Hero.STATS_RARITY[self.rarity][self.grow_spd // 5] + 1
                )
            elif self.bane == Stat.DEF:
                max_def += (
                    Hero.STATS_RARITY[self.rarity][(self.grow_def + 5) // 5]
                    - Hero.STATS_RARITY[self.rarity][self.grow_def // 5] + 1
                )
            elif self.bane == Stat.RES:
                max_res += (
                    Hero.STATS_RARITY[self.rarity][(self.grow_res + 5) // 5]
                    - Hero.STATS_RARITY[self.rarity][self.grow_res // 5] + 1
                )
        bst = max_hp + max_atk + max_spd + max_def + max_res + bonus
        if self.rarity == 5 and self.level == 40:
            duel_skills = [skill.duel_bst for skill in self.equipped
                           if skill.duel_bst]
            if any(duel_skills):
                bst = max(bst, max(duel_skills))
            if self.is_legend and self.legend_boost == LegendStat.DUEL:
                bst = max(bst, 175)
        if self.rarity == 5:
            rfactor = 182
        elif self.rarity == 4:
            rfactor = 168
        elif self.rarity == 3:
            rfactor = 158
        elif self.rarity == 2:
            rfactor = 146
        else:
            rfactor = 136
        sp_score = sum([skill.sp for skill in self.equipped]) // 100 * 2
        return (390 + self.rarity * 4 + rfactor * self.level // 39
                + bst // 5 * 2 + self.merges * 4 + sp_score)

    def learns_skill(self, skill):
        if skill is None:
            return False
        if skill.skill_type == SkillType.WEAPON:
            return skill in [s[0] for s in self.weapon if s[1] and s[1] <= 5]
        if skill.skill_type == SkillType.ASSIST:
            return skill in (s[0] for s in self.assist if s[1] and s[1] <= 5)
        if skill.skill_type == SkillType.SPECIAL:
            return skill in (s[0] for s in self.special if s[1] and s[1] <= 5)
        if skill.skill_type == SkillType.PASSIVE_A:
            return skill in (s[0] for s in self.passive_a
                             if s[1] and s[1] <= 5)
        if skill.skill_type == SkillType.PASSIVE_B:
            return skill in (s[0] for s in self.passive_b
                             if s[1] and s[1] <= 5)
        if skill.skill_type == SkillType.PASSIVE_C:
            return skill in (s[0] for s in self.passive_c
                             if s[1] and s[1] <= 5)
        return False

    def equip(self, skill, *, force_seal=False, fail_fast=False,
              keyword_mode=False, max_rarity=5):
        if keyword_mode and skill.__class__ == str:
            if (skill == 'prf' and self.weapon_prf
                    and not (fail_fast and self.equipped.weapon)):
                self.equipped.weapon = self.weapon_prf
            elif skill == 'summoned':
                if not (fail_fast and self.equipped.weapon):
                    self.equipped.weapon = (
                        next((s[0] for s in self.weapon[::-1]
                              if s[2] and s[2] <= max_rarity), None)
                    )
                if not (fail_fast and self.equipped.assist):
                    self.equipped.assist = (
                        next((s[0] for s in self.assist[::-1]
                              if s[2] and s[2] <= max_rarity), None)
                    )
                if not (fail_fast and self.equipped.special):
                    self.equipped.special = (
                        next((s[0] for s in self.special[::-1]
                              if s[2] and s[2] <= max_rarity), None)
                    )
            elif skill == 'base':
                if not (fail_fast and self.equipped.weapon):
                    self.equipped.weapon = (
                        next((s[0] for s in self.weapon[::-1]
                              if s[1] and s[1] <= max_rarity), None)
                    )
                if not (fail_fast and self.equipped.assist):
                    self.equipped.assist = (
                        next((s[0] for s in self.assist[::-1]
                              if s[1] and s[1] <= max_rarity), None)
                    )
                if not (fail_fast and self.equipped.special):
                    self.equipped.special = (
                        next((s[0] for s in self.special[::-1]
                              if s[1] and s[1] <= max_rarity), None)
                    )
                if not (fail_fast and self.equipped.passive_a):
                    self.equipped.passive_a = (
                        next((s[0] for s in self.passive_a[::-1]
                              if s[1] and s[1] <= max_rarity), None)
                    )
                if not (fail_fast and self.equipped.passive_b):
                    self.equipped.passive_b = (
                        next((s[0] for s in self.passive_b[::-1]
                              if s[1] and s[1] <= max_rarity), None)
                    )
                if not (fail_fast and self.equipped.passive_c):
                    self.equipped.passive_c = (
                        next((s[0] for s in self.passive_c[::-1]
                              if s[1] and s[1] <= max_rarity), None)
                    )
            else:
                return False
            return True
        if (skill is None or self.weapon_type in skill.restrict_set
                or self.move_type in skill.restrict_set
                or (skill.exclusive
                    and self.index not in skill.exclusive_to_id)
            ):
            return False
        if (skill.skill_type == SkillType.WEAPON
                and not (fail_fast and self.equipped.weapon)):
            self.equipped.weapon = skill
        elif (skill.skill_type == SkillType.ASSIST
                and not (fail_fast and self.equipped.assist)):
            self.equipped.assist = skill
        elif (skill.skill_type == SkillType.SPECIAL
                and not (fail_fast and self.equipped.special)):
            self.equipped.special = skill
        elif ((skill.skill_type == SkillType.PASSIVE_SEAL
                or (force_seal and skill.is_seal)
                and not (fail_fast and self.equipped.passive_s))):
            self.equipped.passive_s = skill
        elif skill.skill_type == SkillType.PASSIVE_A:
            if not self.equipped.passive_a:
                self.equipped.passive_a = skill
            elif not self.equipped.passive_s:
                if skill.is_seal:
                    self.equipped.passive_s = skill
                elif self.equipped.passive_a.is_seal:
                    self.equipped.passive_s = self.equipped.passive_a
                    self.equipped.passive_a = skill
                elif not fail_fast:
                    self.equipped.passive_a = skill
            elif not fail_fast:
                self.equipped.passive_a = skill
        elif skill.skill_type == SkillType.PASSIVE_B:
            if not self.equipped.passive_b:
                self.equipped.passive_b = skill
            elif not self.equipped.passive_s:
                if skill.is_seal:
                    self.equipped.passive_s = skill
                elif self.equipped.passive_b.is_seal:
                    self.equipped.passive_s = self.equipped.passive_b
                    self.equipped.passive_b = skill
                elif not fail_fast:
                    self.equipped.passive_b = skill
            elif not fail_fast:
                self.equipped.passive_b = skill
        elif skill.skill_type == SkillType.PASSIVE_C:
            if not self.equipped.passive_c:
                self.equipped.passive_c = skill
            elif not self.equipped.passive_s:
                if skill.is_seal:
                    self.equipped.passive_s = skill
                elif self.equipped.passive_c.is_seal:
                    self.equipped.passive_s = self.equipped.passive_c
                    self.equipped.passive_c = skill
                elif not fail_fast:
                    skill.equipped.passive_c = skill
            elif not fail_fast:
                self.equipped.passive_c = skill
        else:
            return False
        return True

    def get_boons_banes(self):
        boon_hp, boon_atk, boon_spd, boon_def, boon_res = 0, 0, 0, 0, 0
        if (self.boon != Stat.NONE or self.bane != Stat.NONE
                or any(self.equipped) or self.p_hero_id):
            return boon_hp, boon_atk, boon_spd, boon_def, boon_res
        boons = (
            None,
            {10, 25, 40, 55, 70},
            {20, 40, 70},
            set(),
            {10, 70},
            {5, 25, 45, 70},
        )
        banes = (
            None,
            {15, 30, 45, 60, 75},
            {25, 45, 75},
            set(),
            {15, 75},
            {10, 30, 50, 75},
        )
        if self.rarity == 5 or self.rarity == 4:
            if   self.grow_hp  in boons[self.rarity]:
                boon_hp =  1
            elif self.grow_hp  in banes[self.rarity]:
                boon_hp = -1
            if   self.grow_atk in boons[self.rarity]:
                boon_atk =  1
            elif self.grow_atk in banes[self.rarity]:
                boon_atk = -1
            if   self.grow_spd in boons[self.rarity]:
                boon_spd =  1
            elif self.grow_spd in banes[self.rarity]:
                boon_spd = -1
            if   self.grow_def in boons[self.rarity]:
                boon_def =  1
            elif self.grow_def in banes[self.rarity]:
                boon_def = -1
            if   self.grow_res in boons[self.rarity]:
                boon_res =  1
            elif self.grow_res in banes[self.rarity]:
                boon_res = -1
        return boon_hp, boon_atk, boon_spd, boon_def, boon_res

    def reset_merge_order(self):
        self.merge_order = [
            (self.iv_hp , 4, Stat.HP , 0),
            (self.iv_atk, 3, Stat.ATK, 1),
            (self.iv_spd, 2, Stat.SPD, 2),
            (self.iv_def, 1, Stat.DEF, 3),
            (self.iv_res, 0, Stat.RES, 4),
        ]
        self.merge_order.sort(key=lambda sl: (sl[0], sl[1]), reverse = True)
        self.merge_boon = self.boon
        self.merge_bane = self.bane

    def recalc_stats(self):
        '''
        updates max stats from lv1, growth, merges, and rarity
        '''
        self.lv1_hp  = (self.iv_hp  + self.merge_hp + self.rmod_hp
                        + self.df_hp)
        self.lv1_atk = (self.iv_atk + self.merge_atk + self.rmod_atk
                        + self.df_atk + self.p_atk)
        self.lv1_spd = (self.iv_spd + self.merge_spd + self.rmod_spd
                        + self.df_spd + self.p_spd)
        self.lv1_def = (self.iv_def + self.merge_def + self.rmod_def
                        + self.df_def + self.p_def)
        self.lv1_res = (self.iv_res + self.merge_res + self.rmod_res
                        + self.df_res + self.p_res)
        if self.summ_support:
            self.lv1_hp += 3 + self.summ_support // 2
            self.lv1_atk += 2 if self.summ_support >= 4 else 0
            self.lv1_spd += 2 if self.summ_support >= 3 else 0
            self.lv1_def += 2 if self.summ_support >= 2 else 0
            self.lv1_res += 2
        self.max_hp  = (
            self.lv1_hp  + Hero.STATS_RARITY[self.rarity][self.grow_hp // 5])
        self.max_atk = (
            self.lv1_atk + Hero.STATS_RARITY[self.rarity][self.grow_atk // 5])
        self.max_spd = (
            self.lv1_spd + Hero.STATS_RARITY[self.rarity][self.grow_spd // 5])
        self.max_def = (
            self.lv1_def + Hero.STATS_RARITY[self.rarity][self.grow_def // 5])
        self.max_res = (
            self.lv1_res + Hero.STATS_RARITY[self.rarity][self.grow_res // 5])
        if self.merges > 0:
            if self.bane == Stat.NONE:
                pass
            elif self.bane == Stat.HP:
                self.max_hp  += (
                    Hero.STATS_RARITY[self.rarity][(self.grow_hp + 5) // 5]
                    - Hero.STATS_RARITY[self.rarity][self.grow_hp // 5]
                )
            elif self.bane == Stat.ATK:
                self.max_atk += (
                    Hero.STATS_RARITY[self.rarity][(self.grow_atk + 5) // 5]
                    - Hero.STATS_RARITY[self.rarity][self.grow_atk // 5]
                )
            elif self.bane == Stat.SPD:
                self.max_spd += (
                    Hero.STATS_RARITY[self.rarity][(self.grow_spd + 5) // 5]
                    - Hero.STATS_RARITY[self.rarity][self.grow_spd // 5]
                )
            elif self.bane == Stat.DEF:
                self.max_def += (
                    Hero.STATS_RARITY[self.rarity][(self.grow_def + 5) // 5]
                    - Hero.STATS_RARITY[self.rarity][self.grow_def // 5]
                )
            elif self.bane == Stat.RES:
                self.max_res += (
                    Hero.STATS_RARITY[self.rarity][(self.grow_res + 5) // 5]
                    - Hero.STATS_RARITY[self.rarity][self.grow_res // 5]
                )
        self.max_total = (self.max_hp + self.max_atk + self.max_spd
                          + self.max_def + self.max_res)

    def modify_rmod(self, stat_enum, amount):
        '''this is a convenience method to make update_rarity look cleaner'''
        #todo: investigate whether setattr() is faster (it probably isn't)
        if stat_enum == Stat.HP:
            self.rmod_hp  += amount
        elif stat_enum == Stat.ATK:
            self.rmod_atk += amount
        elif stat_enum == Stat.SPD:
            self.rmod_spd += amount
        elif stat_enum == Stat.DEF:
            self.rmod_def += amount
        elif stat_enum == Stat.RES:
            self.rmod_res += amount

    def update_level(self, new_level):
        '''recalculates current stats based on level'''
        raise NotImplementedError("Get me those BVIDs and then we'll talk.")

    def update_rarity(self, new_rarity):
        '''
        recalculates rarity mod from a rarity change
        no more relative calc since base stats saved all the time
        be sure to Hero.recalc_stats() afterwards!
        '''
        if new_rarity < 1:
            new_rarity = 1
        if new_rarity > 5:
            new_rarity = 5
        if new_rarity == self.rarity:
            return
        self.rarity = new_rarity
        modify = 0
        if (new_rarity < 4):
            if new_rarity == 1:
                modify = -2
            else:
                modify = -1
        self.rmod_hp  = modify
        self.rmod_atk = modify
        self.rmod_spd = modify
        self.rmod_def = modify
        self.rmod_res = modify
        if new_rarity % 2 == 1:
            return
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
        if iv is None:
            return
        if increase:
            if iv == Stat.HP:
                self.iv_hp  += 1
                self.grow_hp  += 5
            elif iv == Stat.ATK:
                self.iv_atk += 1
                self.grow_atk += 5
            elif iv == Stat.SPD:
                self.iv_spd += 1
                self.grow_spd += 5
            elif iv == Stat.DEF:
                self.iv_def += 1
                self.grow_def += 5
            elif iv == Stat.RES:
                self.iv_res += 1
                self.grow_res += 5
        else:
            if iv == Stat.HP:
                self.iv_hp  -= 1
                self.grow_hp  -= 5
            elif iv == Stat.ATK:
                self.iv_atk -= 1
                self.grow_atk -= 5
            elif iv == Stat.SPD:
                self.iv_spd -= 1
                self.grow_spd -= 5
            elif iv == Stat.DEF:
                self.iv_def -= 1
                self.grow_def -= 5
            elif iv == Stat.RES:
                self.iv_res -= 1
                self.grow_res -= 5

    def update_ivs(self, boon, bane):
        '''
        recalculates lv1 stats and growths from ivs
        note that this invalidates merge_stat
        '''
        if boon == bane:
            self.modify_iv(self.boon, False)
            self.boon = Stat.NONE
            self.modify_iv(self.bane, True)
            self.bane = Stat.NONE
            return
        if boon is not None and self.boon != boon:
            self.modify_iv(self.boon, False)
            self.modify_iv(boon, True)
            self.boon = boon
        if bane is not None and self.bane != bane:
            self.modify_iv(self.bane, True)
            self.modify_iv(bane, False)
            self.bane = bane
        if self.boon == self.bane:
            self.boon = Stat.NONE
            self.bane = Stat.NONE

    def modify_merge(self, stat_enum, amount):
        '''this is a convenience method to make update_merges look cleaner'''
        #todo: investigate whether setattr() is faster (it probably isn't)
        if stat_enum == Stat.HP:
            self.merge_hp  += amount
        elif stat_enum == Stat.ATK:
            self.merge_atk += amount
        elif stat_enum == Stat.SPD:
            self.merge_spd += amount
        elif stat_enum == Stat.DEF:
            self.merge_def += amount
        elif stat_enum == Stat.RES:
            self.merge_res += amount

    def update_merges(self, new_merges):
        '''
        recalculates lv1 stats from merges
        we do this in a relative manner since its unlikely to be faster
        and updating ivs invalidate previous merge_stat
        be sure to Hero.recalc_stats() afterwards!
        '''
        if new_merges < 0:
            new_merges = 0
        elif new_merges > 10:
            new_merges = 10
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
        if self.merge_boon != self.boon or self.merge_bane != self.bane:
            self.reset_merge_order()
        if self.bane == Stat.NONE and self.boon == Stat.NONE:
            for i in range(3):
                self.modify_merge(self.merge_order[i][2], 1)
        else:
            self.modify_merge(self.bane, 1)
        for i in range(new_merges * 2):
            self.modify_merge(self.merge_order[i % 5][2], 1)

    def update_dragonflowers(self, new_flowers):
        if new_flowers < 0:
            new_flowers = 0
        elif (new_flowers > 5
              and (self.move_type != MoveType.INFANTRY
                   or self.generation > 2)):
            new_flowers = 5
        elif new_flowers > 10:
            new_flowers = 10
        modify = 0
        self.flowers = new_flowers
        if new_flowers == 0:
            self.df_hp  = 0
            self.df_atk = 0
            self.df_spd = 0
            self.df_def = 0
            self.df_res = 0
            return
        if new_flowers == 10:
            modify = 2
            new_flowers = 0
        elif new_flowers >= 5:
            modify = 1
            new_flowers -= 5
        self.df_hp  = modify
        self.df_atk = modify
        self.df_spd = modify
        self.df_def = modify
        self.df_res = modify
        if self.merge_boon != self.boon or self.merge_bane != self.bane:
            self.reset_merge_order()
        for i in range(new_flowers):
            stat_enum = self.merge_order[i % 5][2]
            if stat_enum == Stat.HP:
                self.df_hp  += 1
            elif stat_enum == Stat.ATK:
                self.df_atk += 1
            elif stat_enum == Stat.SPD:
                self.df_spd += 1
            elif stat_enum == Stat.DEF:
                self.df_def += 1
            elif stat_enum == Stat.RES:
                self.df_res += 1

    def update_pair(self, partner):
        self.p_hero_id = partner.index
        self.p_custom = partner.custom_name
        self.p_atk = min((partner.final_atk - 25) // 10, 4)
        self.p_spd = min((partner.final_spd - 10) // 10, 4)
        self.p_def = min((partner.final_def - 10) // 10, 4)
        self.p_res = min((partner.final_res - 10) // 10, 4)

    def force_pair(self, p_hero_id, p_custom, p_atk, p_spd, p_def, p_res):
        self.p_hero_id = p_hero_id
        self.p_custom = p_custom
        self.p_atk = p_atk
        self.p_spd = p_spd
        self.p_def = p_def
        self.p_res = p_res
        self.recalc_stats()

    def unpair(self):
        self.p_hero_id = None
        self.p_custom = None
        self.p_atk = 0
        self.p_spd = 0
        self.p_def = 0
        self.p_res = 0

    def update_stat_mods(
            self, *, boon=None, bane=None, merges=None, rarity=None,
            flowers=None, summ_support=None, pair=None, unpair = False):
        if (boon or bane) and (boon != self.boon or bane != self.bane):
            self.update_ivs(boon, bane)
            update_boons = True
            if merges is None:
                merges = self.merges
            if flowers is None:
                flowers = self.flowers
        else:
            update_boons = False
        if rarity:
            self.update_rarity(rarity)
        if merges is not None:
            self.update_merges(merges)
        if flowers is not None:
            self.update_dragonflowers(flowers)
        if summ_support is not None:
            self.summ_support = max(min(summ_support, 4), 0)
        if unpair:
            self.unpair()
        elif pair is not None:
            self.update_pair(pair)
        if (rarity or update_boons or merges is not None or flowers is not None
                or summ_support is not None or pair is not None or unpair):
            self.recalc_stats()

    def get_merge_table(self):
        '''
        this is slow but kind of annoyingly nested so i couldnt really come up
        with the quick one liner solution, maybe optimize?
        '''
        if self.merge_boon != self.boon or self.merge_bane != self.bane:
            self.reset_merge_order()
        merge_table = [[0, 0, 0, 0, 0]]
        if   self.bane == Stat.NONE:
            for i in range(3):
                merge_table[0][self.merge_order[i][3]] = 1
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
            merge_table[0][self.merge_order[i][3]] += 1
        for i in range(9):
            merge_row = copy(merge_table[i])
            merge_row[self.merge_order[(2 * i + 2) % 5][3]] += 1
            merge_row[self.merge_order[(2 * i + 3) % 5][3]] += 1
            merge_table.append(merge_row)
        return merge_table

    def link(self, unit_lib):
        if self.alt_base_id:
            self.alt_base = unit_lib.get_rhero_by_id(self.alt_base_id)
            self.alt_base.alt_list.append(self)

    def sanity_check(self):
        if   self.rarity == 5:
            stat_total = 47
        elif self.rarity == 4:
            stat_total = 44
        elif self.rarity == 3:
            stat_total = 42
        elif self.rarity == 2:
            stat_total = 39
        elif self.rarity == 1:
            stat_total = 37
        else: print(f'{self.short_name} invalid rarity: {self.rarity}')
        if self.generation < 1 or self.generation > 4:
            print(f'{self.short_name} invalid generation: {self.generation}')
        growth_rate = 255
        ranged = self.weapon_type in {
            UnitWeaponType.R_TOME,
            UnitWeaponType.B_TOME,
            UnitWeaponType.G_TOME,
            UnitWeaponType.C_BOW,
            UnitWeaponType.C_DAGGER,
            UnitWeaponType.C_STAFF,
            UnitWeaponType.R_BOW,
            UnitWeaponType.B_BOW,
            UnitWeaponType.G_BOW,
            UnitWeaponType.R_DAGGER,
            UnitWeaponType.B_DAGGER,
            UnitWeaponType.G_DAGGER,
        }
        ranged_phys = self.weapon_type in {
            UnitWeaponType.C_BOW,
            UnitWeaponType.C_DAGGER,
            UnitWeaponType.R_BOW,
            UnitWeaponType.B_BOW,
            UnitWeaponType.G_BOW,
            UnitWeaponType.R_DAGGER,
            UnitWeaponType.B_DAGGER,
            UnitWeaponType.G_DAGGER,
        }
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
        elif self.move_type == MoveType.CAVALRY:
            stat_total -= 1
            growth_rate -= 5
        if self.is_brave:
            growth_rate += 10
        if (self.generation >= 2
                and not (self.is_dancer and self.generation < 4)):
            stat_total += 1
            growth_rate += 10
            if ranged and self.move_type != MoveType.ARMOR:
                growth_rate -= 5
            if self.move_type == MoveType.CAVALRY:
                stat_total -= 1
                growth_rate -= 5
            elif self.move_type == MoveType.FLIER:
                stat_total -= 1
            if self.is_sigurd:
                growth_rate += 5
            if self.generation >= 3:
                if self.move_type == MoveType.INFANTRY:
                    stat_total += 1
                    growth_rate += 10
                if ranged_phys:
                    stat_total += 1
                    growth_rate += 10
                if self.generation >= 4:
                    stat_total += 2
                    growth_rate += 5
                    if (self.move_type == MoveType.ARMOR
                            or self.move_type == MoveType.CAVALRY):
                        stat_total -= 1
                        growth_rate += 5
                    elif self.move_type == MoveType.FLIER:
                        stat_total += 1
                    if ranged:
                        if self.move_type != MoveType.FLIER:
                            stat_total -= 1
                        else:
                            stat_total -= 2
                        if self.move_type != MoveType.ARMOR:
                            growth_rate += 5
                    if self.is_dancer:
                        growth_rate -= 5

        if self.base_total != stat_total and self.is_enemy < 2:
            print(f'{self.short_name} failed stat total: '
                  f'expected {stat_total} but got {self.base_total}')
        if self.grow_total != growth_rate and self.is_enemy < 2:
            print(f'{self.short_name} failed growth rate: '
                  f'expected {growth_rate} but got {self.grow_total}')
        max_hp  = (self.base_hp
                   + Hero.STATS_RARITY[self.rarity][self.grow_hp // 5])
        if max_hp  != self.max_hp :
            print(f'{self.short_name} failed max hp: '
                  f'expected {max_hp } but got {self.max_hp }')
        max_atk = (self.base_atk
                   + Hero.STATS_RARITY[self.rarity][self.grow_atk // 5])
        if max_atk != self.max_atk:
            print(f'{self.short_name} failed max atk: '
                  f'expected {max_atk} but got {self.max_atk}')
        max_spd  = (self.base_spd
                    + Hero.STATS_RARITY[self.rarity][self.grow_spd // 5])
        if max_spd != self.max_spd:
            print(f'{self.short_name} failed max spd: '
                  f'expected {max_spd} but got {self.max_spd}')
        max_def = (self.base_def
                   + Hero.STATS_RARITY[self.rarity][self.grow_def // 5])
        if max_def != self.max_def:
            print(f'{self.short_name} failed max def: '
                  f'expected {max_def} but got {self.max_def}')
        max_res = (self.base_res
                   + Hero.STATS_RARITY[self.rarity][self.grow_res // 5])
        if max_res != self.max_res:
            print(f'{self.short_name} failed max res: '
                  f'expected {max_res} but got {self.max_res}')


class CombatHero(Hero):
    '''Representation of a unit in combat'''
    pass
