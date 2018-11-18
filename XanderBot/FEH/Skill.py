import asyncio, sqlite3
from FEH.Hero import *
from enum import Enum

class SkillType(Enum):
    '''Enum for each skill typer'''
    WEAPON = 0
    ASSIST = 1
    SPECIAL = 2
    PASSIVE_A = 3
    PASSIVE_B = 4
    PASSIVE_C = 5
    PASSIVE_S = 6

class SpecialTrigger(Enum):
    '''Enum for when specials trigger'''
    UNIT_INITIATE = 0
    UNIT_ATTACK = 1
    UNIT_DEFEND = 2
    UNIT_ASSIST = 3
    UNIQUE_ICE_MIRROR = 4

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
        self.prereq = []
        self.sp = 0
        self.evolvesFrom = []

        #restrictions
        self.moveBlacklist = []
        self.weaponBlacklist = []
        self.moveWhitelist = []
        self.weaponWhitelist = []

        #stats
        self.bonusHP = 0
        self.bonusAtk = 0
        self.bonusSpd = 0
        self.bonusDef = 0
        self.bonusRes = 0
        self.bonusCooldown = 0

        #combat
        self.preCombat = None
        self.postCombat = None

        return self

    @staticmethod
    async def lookup(skillName = 'Null'):
        return('Null')

    def preDeathBlow(h, s):
        h.boostAtkTemp += s.rank * 2

class SpecialSkill(Skill):

    @staticmethod
    async def create(skillName = 'null'):
        self = await Skill.create(skillName)
        
        self.specialCooldown = 2
        self.proc = SpecialTrigger.UNIT_ATTACK
        self.specialProc = None
