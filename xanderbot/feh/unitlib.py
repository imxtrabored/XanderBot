from feh.hero import Hero, Color, WeaponType, MoveType
from feh.hero import LegendElement, Stat
from feh.skill import Skill

class UnitLib(object):
    '''Library of units, loaded into memory'''

    singleton = None

    @classmethod
    async def initialize(cls, sqlite_instance = None):
        print('building unitlib...')
        self = UnitLib()

        self.unit_list = []
        new_hero = Hero('Null', 'Null Hero',
                        Color.RED, WeaponType.R_SWORD, MoveType.INFANTRY,
                        16, 7, 14, 5, 5,
                        55, 50, 50, 50, 50,
                        38, 29, 36, 27, 27,
                        )
        self.unit_list.append(new_hero)
        self.unit_names = dict()
        self.unit_names['null'] = 0
        self.unit_names['zero'] = 0

        self.skill_list = []
        self.skill_list.append(await Skill.create('null'))
        self.skill_names = dict()
        self.skill_names['nullskill'] = 0
        self.skill_names['bestskill'] = 0

        cls.singleton = self
        print('done.')

        return(self)

    @classmethod
    async def get_unitlib(cls):
        if cls.singleton == None:
            await cls.initialize()
        return cls.singleton
