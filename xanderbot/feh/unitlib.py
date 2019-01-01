from copy import copy
from string import punctuation, whitespace

from feh.hero import Hero, Color, UnitWeaponType, MoveType
from feh.hero import LegendElement, Stat
from feh.skill import Skill, SkillType
import sqlite3

transtab = str.maketrans('', '', punctuation + whitespace)

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
        cls.singleton = self
        self.unit_list = []

        new_hero = Hero(0, 'null', 'Null', 'Null', 'Null Hero',
                Color.RED, UnitWeaponType.R_SWORD, MoveType.INFANTRY,
                16, 7, 14, 5, 5,
                55, 50, 50, 50, 50,
                38, 29, 36, 2, 27,
                )
        self.unit_list.append(new_hero)

        for hero in cur:
            new_hero = Hero(*hero)
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
        for skill in cur:
            new_skill = Skill(*skill)
            self.skill_list.append(new_skill)
        #self.skill_list.append(await Skill.create('null'))
        self.skill_names = dict()
        cur.execute("""SELECT * FROM skills_dict;""")
        for index in cur:
            self.skill_names[index[0]] = index[1]
            #print(index[0])

        for skill in self.skill_list[1:]:
            skill.link(self)

        cur.execute("""SELECT * FROM skillsets ORDER BY heroid ASC, unlockRarity ASC, exclusive ASC;""")
        for index in cur:
            hero = self.unit_list[index[0]]
            skill = self.skill_list[index[1]]
            if skill.type == SkillType.WEAPON:
                hero.weapon   .append((skill, index[2], index[3]))
                if skill.exclusive == True: hero.weapon_prf = skill
            elif skill.type == SkillType.ASSIST   :
                hero.assist   .append((skill, index[2], index[3]))
            elif skill.type == SkillType.SPECIAL  :
                hero.special  .append((skill, index[2], index[3]))
            elif skill.type == SkillType.PASSIVE_A:
                hero.passive_a.append((skill, index[2], index[3]))
            elif skill.type == SkillType.PASSIVE_B:
                hero.passive_b.append((skill, index[2], index[3]))
            elif skill.type == SkillType.PASSIVE_C:
                hero.passive_c.append((skill, index[2], index[3]))

            skill.learnable[index[2]].append(hero)
        print('done.')

        return(self)



    @classmethod
    def initialize_emojis(cls, client):
        print('indexing skill emoijs..')
        con = sqlite3.connect("feh/emojis.db", detect_types=sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute("""SELECT * FROM skill_emoji WHERE id > 0 ORDER BY id ASC;""")
        for index in cur:
            skill = cls.singleton.skill_list[index[0]]
            skill.icon = client.get_emoji(int(index[1]))
            if index[2]:
                skill.w_icon = client.get_emoji(int(index[2]))
        
        cur.execute("""SELECT * FROM skill_emoji WHERE id < 0 ORDER BY id DESC;""")
        empty_slots = cur.fetchall()
        Skill.EMPTY_WEAPON   .icon = client.get_emoji(int(empty_slots[0][1]))
        Skill.EMPTY_ASSIST   .icon = client.get_emoji(int(empty_slots[1][1]))
        Skill.EMPTY_SPECIAL  .icon = client.get_emoji(int(empty_slots[2][1]))
        Skill.EMPTY_PASSIVE_A.icon = client.get_emoji(int(empty_slots[3][1]))
        Skill.EMPTY_PASSIVE_B.icon = client.get_emoji(int(empty_slots[4][1]))
        Skill.EMPTY_PASSIVE_C.icon = client.get_emoji(int(empty_slots[5][1]))
        Skill.EMPTY_PASSIVE_S.icon = client.get_emoji(int(empty_slots[6][1]))
        print('done.')



    @staticmethod
    def filter_name(name):
        name = name.replace('+', 'plus')
        name = name.translate(transtab)
        print(name)
        return name



    @classmethod
    def get_hero(cls, hero_name):
        index = cls.singleton.unit_names.get(cls.filter_name(hero_name))
        if index: return copy(cls.singleton.unit_list[index])
        else: return None

      

    @classmethod
    def get_hero_by_id(cls, hero_id):
        return cls.singleton.unit_list[hero_id]



    @classmethod
    def get_skill(cls, skill_name):
        index = cls.singleton.skill_names.get(cls.filter_name(skill_name))
        if index: return cls.singleton.skill_list[index]
        else: return None



    @classmethod
    def get_skill_by_id(cls, skill_id):
        return cls.singleton.skill_list[skill_id]



    @classmethod
    def get_unitlib(cls):
        if cls.singleton == None:
            cls.initialize()
        return cls.singleton
