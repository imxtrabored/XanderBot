from copy import copy
from enum import Enum, unique

from feh.hero import MoveType, UnitWeaponType, SkillType


@unique
class SkillWeaponGroup(Enum):
    NONE     = 0
    R_SWORD  = 1
    R_TOME   = 2
    S_BREATH = 3
    B_LANCE  = 4
    B_TOME   = 5
    G_AXE    = 6
    G_TOME   = 7
    S_BOW    = 8
    S_DAGGER = 9
    C_STAFF  = 10
    S_BEAST  = 11
    S_TOME   = 12

@unique
class SpecialTrigger(Enum):
    '''Enum for when specials trigger'''
    UNIT_INITIATE     = 1
    UNIT_ATTACK       = 2
    UNIT_DEFEND       = 3
    UNIT_POSTCOMBAT   = 4
    UNIT_ASSIST       = 5
    UNIQUE_ICE_MIRROR = 6

@unique
class Refine(Enum):
    EFFECT = 1
    ATK    = 2
    SPD    = 3
    DEF    = 4
    RES    = 5
    STAFF1 = 6
    STAFF2 = 7

effective_types = ()

restrictable_types = (
    MoveType.INFANTRY,
    MoveType.ARMOR   ,
    MoveType.CAVALRY ,
    MoveType.FLIER   ,
    UnitWeaponType.R_SWORD ,
    UnitWeaponType.R_BOW   ,
    UnitWeaponType.R_DAGGER,
    UnitWeaponType.R_TOME  ,
    UnitWeaponType.R_BREATH,
    UnitWeaponType.R_BEAST ,
    UnitWeaponType.B_LANCE ,
    UnitWeaponType.B_BOW   ,
    UnitWeaponType.B_DAGGER,
    UnitWeaponType.B_TOME  ,
    UnitWeaponType.B_BREATH,
    UnitWeaponType.B_BEAST ,
    UnitWeaponType.G_AXE   ,
    UnitWeaponType.G_BOW   ,
    UnitWeaponType.G_DAGGER,
    UnitWeaponType.G_TOME  ,
    UnitWeaponType.G_BREATH,
    UnitWeaponType.G_BEAST ,
    UnitWeaponType.C_BOW   ,
    UnitWeaponType.C_DAGGER,
    UnitWeaponType.C_STAFF ,
    UnitWeaponType.C_BREATH,
    UnitWeaponType.C_BEAST ,
)

class Skill(object):
    '''Represents a skill in FEH'''

    __slots__ = (
        'index', 'identity', 'name', 'description', 'skill_type',
        'weapon_type',
        'is_staff', 'is_seal', 'is_refine', 'is_refined_variant',
        'range', 'might', 'icon', 'w_icon',
        'bonus_hp', 'bonus_atk', 'bonus_spd', 'bonus_def', 'bonus_res',
        'cd_mod', 'special_cd',
        'prereq1', 'prereq1_id', 'prereq2', 'prereq2_id', 'postreq',
        'sp', 'exclusive', 'exclusive_to_id',
        'eff_against', 'eff_set', 'learnable', 'allowed_weapon',
        'restrict_from', 'restrict_set',
        'refinable', 'refined_ver', 'refined_ver_id',
        'refine_sp', 'refine_medals', 'refine_stones', 'refine_dew',
        'refine_eff', 'refine_eff_id', 'refine_st1', 'refine_st1_id',
        'refine_st2', 'refine_st2_id',
        'refine_atk', 'refine_atk_id', 'refine_spd', 'refine_spd_id',
        'refine_def', 'refine_def_id', 'refine_res', 'refine_res_id',
        'refine_path',
        'evolves_to', 'evolves_to_id',
        'evolve_medals', 'evolve_stones', 'evolve_dew',
        'evolves_from', 'evolve_from_id',
        'seal_badge_color', 'seal_great_badges', 'seal_small_badges',
        'seal_coins',
        'skill_rank', 'tier', 'duel_bst'
    )

    def __init__(
            self, index, identity, name, description, skill_type,
            weapon_type = 0,
            staff_exclusive = False, is_seal = False, is_refine = False,
            is_refined_variant = False, range = 0, might = 0,
            bonus_hp = 0, bonus_atk = 0, bonus_spd = 0, bonus_def = 0,
            bonus_res = 0, cd_mod = 0, special_cd = 0,
            prereq1 = False, prereq2 = False, sp = 0, exclusive = False,
            eff_infantry = False, eff_armor = False, eff_cavalry = False,
            eff_flier = False,
            eff_r_sword = False, eff_b_lance = False ,eff_g_axe = False,
            eff_r_bow = False, eff_b_bow = False, eff_g_bow = False,
            eff_c_bow = False, eff_r_dagger = False, eff_b_dagger = False,
            eff_g_dagger = False, eff_c_dagger = False, eff_r_tome = False,
            eff_b_tome = False, eff_g_tome = False, eff_c_staff = False,
            eff_r_breath = False, eff_b_breath = False, eff_g_breath = False,
            eff_c_breath = False, eff_r_beast = False, eff_b_beast = False,
            eff_g_beast = False, eff_c_beast = False,
            infantry = True, armor = True, cavalry = True, flier = True,
            r_sword = True, b_lance = True, g_axe = True, r_bow = True,
            b_bow = True, g_bow = True, c_bow = True, r_dagger = True,
            b_dagger = True, g_dagger = True, c_dagger = True, r_tome = True,
            b_tome = True, g_tome = True, c_staff = True, r_breath = True,
            b_breath = True, g_breath = True, c_breath = True,
            r_beast = True, b_beast = True, g_beast = True, c_beast = True,
            refinable = None, refined_version = None, refine_sp = None,
            refine_medals = 0, refine_stones = 0, refine_dew = 0,
            refine_eff = None, refine_st1 = None, refine_st2 = None,
            refine_atk = None, refine_spd = None, refine_def = None,
            refine_res = None,
            evolves_to = None, evolve_medals = 0, evolve_stones = 0,
            evolve_dew = 0, evolve_from = None,
            seal_badge_color = 1, seal_great_badges = 0, seal_small_badges = 0,
            seal_coins = 0,
            skill_rank = 0, tier = 0, duel_bst = None
    ):
        '''theres no way to make this look pretty is there haw haw haw'''

        #initialize skill name
        self.index = index
        self.identity = identity
        self.name = name
        self.description = description if description else ''
        self.skill_type = SkillType(skill_type)
        self.weapon_type = (SkillWeaponGroup(weapon_type) if weapon_type
                            else None)
        self.icon = ''
        self.w_icon = ''
        self.skill_rank = skill_rank
        self.tier = tier
        self.duel_bst = duel_bst

        self.is_staff = staff_exclusive
        self.is_seal = is_seal
        self.is_refine = is_refine
        self.is_refined_variant = is_refined_variant

        #display
        self.range        = range
        self.might        = might

        #stats
        self.bonus_hp   = bonus_hp
        self.bonus_atk  = bonus_atk
        self.bonus_spd  = bonus_spd
        self.bonus_def  = bonus_def
        self.bonus_res  = bonus_res
        self.cd_mod     = cd_mod
        self.special_cd = special_cd

        #prereq
        self.prereq1_id = prereq1
        self.prereq2_id = prereq2
        self.prereq1 = None
        self.prereq2 = None
        self.postreq = []
        self.sp = sp
        self.exclusive = exclusive
        self.exclusive_to_id = set()

        #effective
        effective = (
            eff_infantry,
            eff_armor   ,
            eff_cavalry ,
            eff_flier   ,
            eff_r_sword ,
            eff_r_bow   ,
            eff_r_dagger,
            eff_r_tome  ,
            eff_r_breath,
            eff_r_beast ,
            eff_b_lance ,
            eff_b_bow   ,
            eff_b_dagger,
            eff_b_tome  ,
            eff_b_breath,
            eff_b_beast ,
            eff_g_axe   ,
            eff_g_bow   ,
            eff_g_dagger,
            eff_g_tome  ,
            eff_g_breath,
            eff_g_beast ,
            eff_c_bow   ,
            eff_c_dagger,
            eff_c_staff ,
            eff_c_breath,
            eff_c_beast ,
        )
        self.eff_against = [
            restrictable_types[i]
            for i, val in enumerate(effective)
            if val
        ]
        self.eff_set = set(self.eff_against)

        #learnable
        self.learnable = (
            None,
            [],
            [],
            [],
            [],
            [],
        )

        #restrictions
        allowed_weapon = (
            r_sword ,
            r_bow   ,
            r_dagger,
            r_tome  ,
            r_breath,
            r_beast ,
            b_lance ,
            b_bow   ,
            b_dagger,
            b_tome  ,
            b_breath,
            b_beast ,
            g_axe   ,
            g_bow   ,
            g_dagger,
            g_tome  ,
            g_breath,
            g_beast ,
            c_bow   ,
            c_dagger,
            c_staff ,
            c_breath,
            c_beast ,
        )
        self.allowed_weapon = [
            restrictable_types[i + 4]
            for i, val in enumerate(allowed_weapon)
            if val
        ]
        allowed = (
            infantry,
            armor   ,
            cavalry ,
            flier   ,
            r_sword ,
            r_bow   ,
            r_dagger,
            r_tome  ,
            r_breath,
            r_beast ,
            b_lance ,
            b_bow   ,
            b_dagger,
            b_tome  ,
            b_breath,
            b_beast ,
            g_axe   ,
            g_bow   ,
            g_dagger,
            g_tome  ,
            g_breath,
            g_beast ,
            c_bow   ,
            c_dagger,
            c_staff ,
            c_breath,
            c_beast ,
        )
        self.restrict_from = [
            restrictable_types[i]
            for i, val in enumerate(allowed)
            if not val
        ]
        self.restrict_set = set(self.restrict_from)

        #refines
        self.refinable      = refinable
        self.refined_ver_id = refined_version
        self.refined_ver    = None
        self.refine_sp      = refine_sp
        self.refine_medals  = refine_medals
        self.refine_stones  = refine_stones
        self.refine_dew     = refine_dew
        self.evolves_to_id  = evolves_to
        self.evolves_to     = None
        self.evolve_medals  = evolve_medals
        self.evolve_stones  = evolve_stones
        self.evolve_dew     = evolve_dew
        self.evolve_from_id = evolve_from
        self.evolves_from   = None
        self.refine_eff_id  = refine_eff
        self.refine_eff     = None
        self.refine_st1_id  = refine_st1
        self.refine_st1     = None
        self.refine_st2_id  = refine_st2
        self.refine_st2     = None
        self.refine_atk_id  = refine_atk
        self.refine_atk     = None
        self.refine_spd_id  = refine_spd
        self.refine_spd     = None
        self.refine_def_id  = refine_def
        self.refine_def     = None
        self.refine_res_id  = refine_res
        self.refine_res     = None
        self.refine_path    = None

        self.seal_badge_color  = seal_badge_color
        self.seal_great_badges = seal_great_badges
        self.seal_small_badges = seal_small_badges
        self.seal_coins        = seal_coins

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.index == other.index
        return NotImplemented

    def get_refine(self, refine):
        if refine == Refine.EFFECT:
            return self.refine_eff
        elif refine == Refine.ATK:
            return self.refine_atk
        elif refine == Refine.SPD:
            return self.refine_spd
        elif refine == Refine.DEF:
            return self.refine_def
        elif refine == Refine.RES:
            return self.refine_res
        elif refine == Refine.STAFF1:
            return self.refine_st1
        elif refine == Refine.STAFF2:
            return self.refine_st2
        else:
            return None

    def get_refined(self, refine):
        if refine is None: return
        skill = copy(self)
        if skill.refined_ver:
            skill.description = skill.refined_ver.description
            skill.might = skill.refined_ver.might
            skill.bonus_atk = skill.refined_ver.bonus_atk
            skill.refined_ver = None
            skill.refined_ver_id = None
        if (refine == skill.refine_eff or refine == skill.refine_st1
                or refine == skill.refine_st2):
            skill.description = (
                f'{self.description}\n{refine.icon}: **{refine.description}**')
        skill.bonus_hp += refine.bonus_hp
        skill.might += refine.bonus_atk
        skill.bonus_atk += refine.bonus_atk
        skill.bonus_spd += refine.bonus_spd
        skill.bonus_def += refine.bonus_def
        skill.bonus_res += refine.bonus_res
        temp = skill.sp
        skill.sp = skill.refine_sp
        skill.refine_sp = temp
        skill.icon = refine.icon
        skill.refine_path = refine
        return skill

    def set_tier_recursive(self):
        if self.tier:
            return self.tier + 1
        if not self.prereq1:
            self.tier = 1
        else:
            self.tier = self.prereq1.set_tier_recursive()
        if self.prereq2:
            self.tier = min(self.tier, self.prereq2.set_tier_recursive())
        return self.tier + 1

    def get_cumul_sp_recursive(self):
        refine_sp = self.refine_sp if self.refine_path else 0
        if not self.prereq1:
            return self.sp + refine_sp
        else:
            return self.prereq1.get_cumul_sp_recursive() + self.sp + refine_sp

    def get_cumul_sp_hero_recur(self, hero):
        self_sp = self.sp if hero.learns_skill(self) else self.sp * 3 // 2
        if self.refine_path:
            refine_sp = (self.refine_sp if hero.learns_skill(self)
                         else self.refine_sp * 3 // 2)
        else:
            refine_sp = 0
        if not self.prereq1:
            return self_sp + refine_sp
        else:
            if self.prereq2:
                if hero.learns_skill(self.evolves_from):
                    # KLUDGE KLUDGE FIX ME
                    return min(
                        self.prereq1.get_cumul_sp_hero_recur(hero)
                        + self_sp + refine_sp,
                        self.prereq2.get_cumul_sp_hero_recur(hero)
                        + self.sp + min(refine_sp, self.refine_sp)
                    )
                return (min(self.prereq1.get_cumul_sp_hero_recur(hero),
                            self.prereq2.get_cumul_sp_hero_recur(hero))
                        + self_sp + refine_sp)
            return (self.prereq1.get_cumul_sp_hero_recur(hero)
                    + self_sp + refine_sp)

    def link(self, unit_lib):
        if self.prereq1_id:
            self.prereq1 = unit_lib.get_rskill_by_id(self.prereq1_id)
            self.prereq1.postreq.append(self)
        if self.prereq2_id:
            self.prereq2 = unit_lib.get_rskill_by_id(self.prereq2_id)
            self.prereq2.postreq.append(self)
        if self.evolves_to_id:
            self.evolves_to = unit_lib.get_rskill_by_id(self.evolves_to_id)
            self.evolves_to.evolves_from = self
        if self.refined_ver_id:
            self.refined_ver = unit_lib.get_rskill_by_id(self.refined_ver_id)
        if self.refine_eff_id:
            self.refine_eff = unit_lib.get_rskill_by_id(self.refine_eff_id)
        if self.refine_st1_id:
            self.refine_st1 = unit_lib.get_rskill_by_id(self.refine_st1_id)
        if self.refine_st2_id:
            self.refine_st2 = unit_lib.get_rskill_by_id(self.refine_st2_id)
        if self.refine_atk_id:
            self.refine_atk = unit_lib.get_rskill_by_id(self.refine_atk_id)
        if self.refine_spd_id:
            self.refine_spd = unit_lib.get_rskill_by_id(self.refine_spd_id)
        if self.refine_def_id:
            self.refine_def = unit_lib.get_rskill_by_id(self.refine_def_id)
        if self.refine_res_id:
            self.refine_res = unit_lib.get_rskill_by_id(self.refine_res_id)

Skill.EMPTY_WEAPON = Skill(
    -1, 'null weapon', 'None', 'Empty weapon slot',
    SkillType.WEAPON
)
Skill.EMPTY_ASSIST = Skill(
    -2, 'null assist', 'None', 'Empty assist slot',
    SkillType.ASSIST
)
Skill.EMPTY_SPECIAL = Skill(
    -3, 'null special', 'None', 'Empty special slot',
    SkillType.SPECIAL
)
Skill.EMPTY_PASSIVE_A = Skill(
    -4, 'null passive a', 'None', 'Empty A passive slot',
    SkillType.PASSIVE_A
)
Skill.EMPTY_PASSIVE_B = Skill(
    -5, 'null passive b', 'None', 'Empty B passive slot',
    SkillType.PASSIVE_B
)
Skill.EMPTY_PASSIVE_C = Skill(
    -6, 'null passive c', 'None', 'Empty C passive slot',
    SkillType.PASSIVE_C
)
Skill.EMPTY_PASSIVE_S = Skill(
    -7, 'null passive s', 'None', 'Empty Sacred Seal slot',
    SkillType.PASSIVE_SEAL
)


class SpecialSkill(Skill):

    pass
