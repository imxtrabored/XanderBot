from feh.hero import Hero, Color, UnitWeaponType, MoveType
from feh.hero import LegendElement, Stat
from feh.skill import Skill
import sqlite3

class UnitLib(object):
    '''Library of units, loaded into memory'''

    singleton = None

    @classmethod
    def initialize(cls, sqlite_instance = None):
        print('building unitlib...')
        '''
        sqlite3.register_converter('color', Color)
        sqlite3.register_converter('weapon_type', WeaponType)
        sqlite3.register_converter('move_type', MoveType)
        '''

        con = sqlite3.connect("feh/fehdata.db", detect_types=sqlite3.PARSE_COLNAMES)
        cur = con.cursor()

        cur.execute("""SELECT * FROM hero ORDER BY id ASC;""")

        self = UnitLib()
        self.unit_list = []

        new_hero = Hero('Null', 'Null Hero',
                Color.RED, UnitWeaponType.R_SWORD, MoveType.INFANTRY,
                16, 7, 14, 5, 5,
                55, 50, 50, 50, 50,
                38, 29, 36, 2, 27,
                )
        self.unit_list.append(new_hero)

        for hero in cur:
            new_hero = Hero(*hero[2:])
            self.unit_list.append(new_hero)


        self.unit_names = dict()
        self.unit_names['null'] = 0
        self.unit_names['zero'] = 0

        cur.execute("""SELECT * FROM hero_dict;""")
        for index in cur:
            self.unit_names[index[0]] = index[1]
            #print(index[0])

        cur.execute("""SELECT * FROM skills ORDER BY id ASC;""")

        self.skill_list = []
        self.skill_list.append(None)
        for skill in cur:
            new_skill = Skill(*skill)
            self.skill_list.append(new_skill)
        #self.skill_list.append(await Skill.create('null'))
        self.skill_names = dict()
        cur.execute("""SELECT * FROM skills_dict;""")
        for index in cur:
            self.skill_names[index[0]] = index[1]
            #print(index[0])

        cls.singleton = self
        print('done.')

        return(self)

    @classmethod
    async def get_unitlib(cls):
        if cls.singleton == None:
            await cls.initialize()
        return cls.singleton
