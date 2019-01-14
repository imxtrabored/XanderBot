from enum import Enum, unique

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

@unique
class SpecialTrigger(Enum):
    '''Enum for when specials trigger'''
    UNIT_INITIATE     = 1
    UNIT_ATTACK       = 2
    UNIT_DEFEND       = 3
    UNIT_POSTCOMBAT   = 4
    UNIT_ASSIST       = 5
    UNIQUE_ICE_MIRROR = 6

class Skill(object):
    '''Represents a skill in FEH'''

    __slots__ = (
        'id', 'identity', 'name', 'description', 'type', 'weapon_type',
        'is_staff', 'is_seal', 'is_refine', 'is_refined_variant',
        'range', 'disp_atk', 'icon', 'w_icon',
        'eff_infantry', 'eff_armor', 'eff_cavalry', 'eff_flier',
        'eff_magic', 'eff_dragon',
        'bonus_hp', 'bonus_atk', 'bonus_spd', 'bonus_def', 'bonus_res',
        'cd_mod', 'special_cd',
        'prereq1', 'prereq1_id', 'prereq2', 'prereq2_id', 'postreq',
        'sp', 'exclusive', 'learnable',
        'infantry', 'armor', 'cavalry', 'flier',
        'r_sword', 'r_tome', 'r_breath', 'b_lance', 'b_tome', 'b_breath',
        'g_axe', 'g_tome', 'g_breath', 'c_bow', 'c_dagger', 'c_staff',
        'c_breath', 'r_bow', 'b_bow', 'g_bow', 'r_dagger', 'b_dagger',
        'g_dagger', 'r_beast', 'b_beast', 'g_beast', 'c_beast', 'allowed',
        'refinable', 'refined_version', 'refined_version_id',
        'refine_sp', 'refine_medals', 'refine_stones', 'refine_dew',
        'refine_eff', 'refine_eff_id', 'refine_staff1', 'refine_staff1_id',
        'refine_staff2', 'refine_staff2_id',
        'refine_atk', 'refine_atk_id', 'refine_spd', 'refine_spd_id',
        'refine_def', 'refine_def_id', 'refine_res', 'refine_res_id',
        'evolves_to', 'evolves_to_id',
        'evolve_medals', 'evolve_stones', 'evolve_dew',
        'evolves_from', 'evolves_from_id',
        'seal_badge_color', 'seal_great_badges', 'seal_small_badges',
        'seal_coins',
        'skill_rank', 'tier',
        'fn_pre_combat', 'fn_on_attack', 'fn_on_defend',
        'fn_post_combat', 'fn_on_assist' 
    )

    def __init__(
            self, id, identity, name, description, type, weapon_type = 0,
            staff_exclusive = False, is_seal = False, is_refine = False,
            is_refined_variant = False, range = 0, disp_atk = 0,
            eff_infantry = False, eff_armor = False, eff_cavalry = False,
            eff_flier = False, eff_magic = False, eff_dragon = False,
            bonus_hp = 0, bonus_atk = 0, bonus_spd = 0, bonus_def = 0,
            bonus_res = 0, cd_mod = 0, special_cd = 0,
            prereq1 = False, prereq2 = False, sp = 0, exclusive = False,
            infantry = True, armor = True, cavalry = True, flier = True,
            r_sword = True, r_tome = True, r_breath = True, b_lance = True,
            b_tome = True, b_breath = True, g_axe = True, g_tome = True,
            g_breath = True, c_bow = True, c_dagger = True, c_staff = True,
            c_breath = True, r_bow = True, b_bow = True, g_bow = True,
            r_dagger = True, b_dagger = True, g_dagger = True,
            r_beast = True, b_beast = True, g_beast = True, c_beast = True,
            refinable = None, refined_version = None, refine_sp = None,
            refine_medals = 0, refine_stones = 0, refine_dew = 0,
            refine_eff = None, refine_staff1 = None, refine_staff2 = None,
            refine_atk = None, refine_spd = None, refine_def = None,
            refine_res = None,
            evolves_to = None, evolve_medals = 0, evolve_stones = 0,
            evolve_dew = 0, evolves_from = None,
            seal_badge_color = 1, seal_great_badges = 0, seal_small_badges = 0,
            seal_coins = 0,
            skill_rank = 0, tier = 0,
            fn_pre_combat = False, fn_on_attack = False, fn_on_defend =
            False, fn_post_combat = False, fn_on_assist = False
    ):
        '''theres no way to make this look pretty is there haw haw haw'''

        #initialize skill name
        self.id = id
        self.identity = identity
        self.name = name
        self.description = description if description else ''
        self.type = SkillType(type)
        self.weapon_type = (SkillWeaponGroup(weapon_type) if weapon_type
                            else None)
        self.icon = ''
        self.w_icon = ''
        self.skill_rank = skill_rank
        self.tier = tier

        self.is_staff = staff_exclusive
        self.is_seal = is_seal
        self.is_refine = is_refine
        self.is_refined_variant = is_refined_variant

        #display
        self.range        = range
        self.disp_atk     = disp_atk
        self.eff_infantry = eff_infantry
        self.eff_armor    = eff_armor
        self.eff_cavalry  = eff_cavalry
        self.eff_flier    = eff_flier
        self.eff_magic    = eff_magic
        self.eff_dragon   = eff_dragon

        #stats
        self.bonus_hp  = bonus_hp
        self.bonus_atk = bonus_atk
        self.bonus_spd = bonus_spd
        self.bonus_def = bonus_def
        self.bonus_res = bonus_res
        self.cd_mod    = cd_mod
        self.special_cd = special_cd

        #prereq
        self.prereq1_id = prereq1
        self.prereq2_id = prereq2
        self.prereq1 = None
        self.prereq2 = None
        self.postreq = []
        self.sp = sp
        self.exclusive = exclusive

        #learnable
        self.learnable = [
            None,
            [],
            [],
            [],
            [],
            []
        ]

        #restrictions
        '''
        self.move_blacklist = []
        self.weapon_blacklist = []
        self.move_whitelist = []
        self.weapon_whitelist = []
        '''
        self.infantry = infantry
        self.armor    = armor
        self.cavalry  = cavalry
        self.flier    = flier
        self.r_sword  = r_sword
        self.r_tome   = r_tome
        self.r_breath = r_breath
        self.b_lance  = b_lance
        self.b_tome   = b_tome
        self.b_breath = b_breath
        self.g_axe    = g_axe
        self.g_tome   = g_tome
        self.g_breath = g_breath
        self.c_bow    = c_bow
        self.c_dagger = c_dagger
        self.c_staff  = c_staff
        self.c_breath = c_breath
        self.r_bow    = r_bow
        self.b_bow    = b_bow
        self.g_bow    = g_bow
        self.r_dagger = r_dagger
        self.b_dagger = b_dagger
        self.g_dagger = g_dagger
        self.r_beast  = r_beast
        self.b_beast  = b_beast
        self.g_beast  = g_beast
        self.c_beast  = c_beast

        self.allowed = (
            infantry,
            armor   ,
            cavalry ,
            flier   ,
            r_sword ,
            r_tome  ,
            r_dagger,
            r_bow   ,
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


        #refines
        #self.refines = []
        self.refinable          = refinable
        self.refined_version_id = refined_version
        self.refined_version    = None
        self.refine_sp          = refine_sp
        self.refine_medals      = refine_medals
        self.refine_stones      = refine_stones
        self.refine_dew         = refine_dew
        self.evolves_to_id      = evolves_to
        self.evolves_to         = None
        self.evolve_medals      = evolve_medals
        self.evolve_stones      = evolve_stones
        self.evolve_dew         = evolve_dew
        self.evolves_from_id    = evolves_from
        self.evolves_from       = None
        self.refine_eff_id      = refine_eff
        self.refine_eff         = None
        self.refine_staff1_id   = refine_staff1
        self.refine_staff1      = None
        self.refine_staff2_id   = refine_staff2
        self.refine_staff2      = None
        self.refine_atk_id      = refine_atk
        self.refine_atk         = None
        self.refine_spd_id      = refine_spd
        self.refine_spd         = None
        self.refine_def_id      = refine_def
        self.refine_def         = None
        self.refine_res_id      = refine_res
        self.refine_res         = None

        self.seal_badge_color  = seal_badge_color
        self.seal_great_badges = seal_great_badges
        self.seal_small_badges = seal_small_badges
        self.seal_coins        = seal_coins

        #combat
        #self.pre_combat = None
        #self.post_combat = None



    def set_tier_recursive(self):
        if self.tier: return self.tier + 1
        if not self.prereq1:
            self.tier = 1
        else: self.tier = self.prereq1.set_tier_recursive()
        if self.prereq2: self.prereq2.set_tier_recursive()
        # if self.tier > 3 and self.type != SkillType.WEAPON: print(self.name)
        # if self.tier >= 3 and self.name.endswith('2'): print(self.name)
        return self.tier + 1



    def get_cumul_sp_recursive(self):
        if not self.prereq1: return self.sp
        else: return self.prereq1.get_cumul_sp_recursive() + self.sp



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
        # if self.evolves_from_id   : self.evolves_from    = unit_lib.get_skill_by_id(self.evolves_from_id   )
        if self.refined_version_id:
            self.refined_version = unit_lib.get_rskill_by_id(self.refined_version_id)
        if self.refine_eff_id     :
            self.refine_eff      = unit_lib.get_rskill_by_id(self.refine_eff_id     )
        if self.refine_staff1_id  :
            self.refine_staff1   = unit_lib.get_rskill_by_id(self.refine_staff1_id  )
        if self.refine_staff2_id  :
            self.refine_staff2   = unit_lib.get_rskill_by_id(self.refine_staff2_id  )
        if self.refine_atk_id     :
            self.refine_atk      = unit_lib.get_rskill_by_id(self.refine_atk_id     )
        if self.refine_spd_id     :
            self.refine_spd      = unit_lib.get_rskill_by_id(self.refine_spd_id     )
        if self.refine_def_id     :
            self.refine_def      = unit_lib.get_rskill_by_id(self.refine_def_id     )
        if self.refine_res_id     :
            self.refine_res      = unit_lib.get_rskill_by_id(self.refine_res_id     )
        # note: replace this error checking line
        # if self.prereq1 == self: print(self.name+', '+str(self.prereq1_id-1))

        self.set_tier_recursive()



Skill.EMPTY_WEAPON    = Skill(
    -1, 'null weapon'   , 'None', 'Empty weapon slot'     ,
    SkillType.WEAPON
)
Skill.EMPTY_ASSIST    = Skill(
    -2, 'null assist'   , 'None', 'Empty assist slot'     ,
    SkillType.ASSIST
)
Skill.EMPTY_SPECIAL   = Skill(
    -3, 'null special'  , 'None', 'Empty special slot'    ,
    SkillType.SPECIAL
)
Skill.EMPTY_PASSIVE_A = Skill(
    -4, 'null passive a', 'None', 'Empty A passive slot'  ,
    SkillType.PASSIVE_A
)
Skill.EMPTY_PASSIVE_B = Skill(
    -5, 'null passive b', 'None', 'Empty B passive slot'  ,
    SkillType.PASSIVE_B
)
Skill.EMPTY_PASSIVE_C = Skill(
    -6, 'null passive c', 'None', 'Empty C passive slot'  ,
    SkillType.PASSIVE_C
)
Skill.EMPTY_PASSIVE_S = Skill(
    -7, 'null passive s', 'None', 'Empty Sacred Seal slot',
    SkillType.PASSIVE_SEAL
)



class SpecialSkill(Skill):

    pass
