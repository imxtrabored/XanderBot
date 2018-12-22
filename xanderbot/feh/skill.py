import asyncio, sqlite3
from enum import Enum, unique

@unique
class SkillType(Enum):
    '''Enum for each skill type'''
    NONE = 0
    WEAPON = 1
    ASSIST = 2
    SPECIAL = 3
    PASSIVE_A = 4
    PASSIVE_B = 5
    PASSIVE_C = 6
    PASSIVE_SEAL = 7
    WEAPON_REFINED = 8
    REFINE = 9

@unique
class SkillWeaponGroup(Enum):
    NONE = 0
    R_SWORD = 1
    R_TOME = 2
    S_BREATH =3
    B_LANCE = 4
    B_TOME = 5
    G_AXE = 6
    G_TOME = 7
    S_BOW = 8
    S_DAGGER = 9
    C_STAFF = 10

@unique
class SpecialTrigger(Enum):
    '''Enum for when specials trigger'''
    UNIT_INITIATE = 1
    UNIT_ATTACK = 2
    UNIT_DEFEND = 3
    UNIT_POSTCOMBAT = 4
    UNIT_ASSIST = 5
    UNIQUE_ICE_MIRROR = 6

class Skill(object):
    '''Represents a skill in FEH'''

    def __init__(self, id, identity, name, description, type, weapon_type, 
                 staff_exclusive,  is_seal, is_refine, is_refined_variant,
                 range, disp_atk, eff_infantry, eff_armor, eff_cavalry,
                 eff_flier, eff_magic, eff_dragon, bonus_hp, bonus_atk,
                 bonus_spd, bonus_def, bonus_res, cd_mod, prereq1, prereq2,
                 sp, exclusive, infantry, armor, cavalry, flier, r_sword,
                 r_tome, r_breath, b_lance, b_tome, b_breath, g_axe, g_tome,
                 g_breath, c_bow, c_dagger, c_staff, c_breath, r_bow, b_bow,
                 g_bow, r_dagger, b_dagger, g_dagger, refinable,
                 refined_version, refine_sp, evolves_to, evolves_from,
                 refine_eff, refine_staff1, refine_staff2, refine_atk,
                 refine_spd, refine_def, refine_res, special_cd, rank,
                 fn_pre_combat, fn_on_attack, fn_on_defend, fn_post_combat,
                 fn_on_assist
                 ):
        '''theres no way to make this look pretty is there'''

        #initialize skill name
        self.name = name
        self.description = description
        self.type = SkillType(type)
        if weapon_type: self.weapon_type = SkillWeaponGroup(weapon_type)
        self.rank = 3

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

        #prereq
        self.prereq1 = prereq1
        self.prereq2 = prereq2
        self.postreq = (None)
        self.sp = sp
        self.exclusive = exclusive
        self.evolves_from = [self]

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


        #refines
        #self.refines = []
        self.refinable       = refinable      
        self.refined_version = refined_version
        self.refine_sp       = refine_sp      
        self.evolves_to      = evolves_to     
        self.evolves_from    = evolves_from   
        self.refine_eff      = refine_eff     
        self.refine_staff1   = refine_staff1
        self.refine_staff2   = refine_staff2
        self.refine_atk      = refine_atk     
        self.refine_spd      = refine_spd     
        self.refine_def      = refine_def     
        self.refine_res      = refine_res     

        #combat
        self.pre_combat = None
        self.post_combat = None


    def pre_death_blow(h, s):
        return

class SpecialSkill(Skill):

    @staticmethod
    async def create(skill_name = 'null'):
        self = await Skill.create(skill_name)
        
        self.special_cooldown = 2
        self.proc = SpecialTrigger.UNIT_ATTACK
        self.special_proc = None
