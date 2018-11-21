import sqlite3
from feh.hero import Hero
from feh.skill import Skill

class UnitLib(object):
    '''Library of units, loaded into memory'''

    @staticmethod
    async def initialize(sqlite_instance = None):
        self = UnitLib()

        self.unit_list = []
        self.unit_list.append(await Hero.create('null'))
        self.unit_names = dict()
        self.unit_names['null'] = 0
        self.unit_names['zero'] = 0

        self.skill_list = []
        self.skill_list.append(await Skill.create('null'))
        self.skill_names = dict()
        self.skill_names['nullskill'] = 0
        self.skill_names['bestskill'] = 0
        return(self)