import asyncio, sqlite3
from enum import Enum

class SkillType(Enum):
    '''Enum for each skill typer'''
    WEAPON = 1
    ASSIST = 2
    SPECIAL = 3
    PASSIVE_A = 4
    PASSIVE_B = 5
    PASSIVE_C = 6
    PASSIVE_S = 7

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

    @staticmethod
    async def create(skillName = 'null'):
        '''Temporary init; will replace with sqlite lookup'''
        self = Skill()

        #initialize skill name
        self.name = 'NullSkill'
        self.description = 'Does some stuff to skills and damage'
        self.type = SkillType.PASSIVE_A
        self.rank = 3

        #prereq
        self.prereq = [self]
        self.postreq = [self]
        self.sp = 0
        self.evolves_from = [self]

        #restrictions
        self.move_blacklist = []
        self.weapon_blacklist = []
        self.move_whitelist = []
        self.weapon_whitelist = []

        #stats
        self.bonus_hp = 0
        self.bonus_atk = 0
        self.bonus_spd = 0
        self.bonus_def = 0
        self.bonus_res = 0
        self.bonus_cooldown = 0

        self.refines = []

        #combat
        self.pre_combat = None
        self.post_combat = None

        return self

    def pre_death_blow(h, s):
        return

class SpecialSkill(Skill):

    @staticmethod
    async def create(skill_name = 'null'):
        self = await Skill.create(skill_name)
        
        self.special_cooldown = 2
        self.proc = SpecialTrigger.UNIT_ATTACK
        self.special_proc = None
