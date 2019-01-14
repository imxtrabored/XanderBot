from copy import copy
from string import punctuation, whitespace

from feh.hero import Hero, Color, UnitWeaponType, MoveType
from feh.skill import Skill, SkillType
import sqlite3

transtab = str.maketrans('', '', punctuation + whitespace)

class UnitLib(object):
    '''Library of units, loaded into memory'''

    singleton = None

    @classmethod
    def initialize(cls):
        print('building unitlib...')
        '''
        sqlite3.register_converter('color', Color)
        sqlite3.register_converter('weapon_type', WeaponType)
        sqlite3.register_converter('move_type', MoveType)
        '''

        con = sqlite3.connect("feh/fehdata.db", detect_types=sqlite3.PARSE_COLNAMES)
        cur = con.cursor()

        cur.execute(
            """SELECT id, identity, name, short_name, epithet, color,
            weapon_type, move_type, base_hp, base_atk, base_spd, base_def,
            base_res, grow_hp, grow_atk, grow_spd, grow_def, grow_res,
            max_hp, max_atk, max_spd, max_def, max_res, is_legend,
            legend_element, legend_boost, tome_type, description, bvid,
            artist, vo_en, vo_jp, alt_base_id, is_story, is_seasonal,
            is_grail, is_veteran, is_trainee, is_dancer, is_brave,
            is_sigurd, generation
            FROM hero ORDER BY id ASC;"""
        )

        self = UnitLib()
        cls.singleton = self
        self.unit_list = []

        new_hero = Hero(
            0, 'null', 'Null', 'Null', 'Null Hero',
            Color.RED, UnitWeaponType.R_SWORD, MoveType.INFANTRY,
            16, 7, 14, 5, 5,
            55, 50, 50, 50, 50,
            40, 29, 36, 27, 27,
        )
        self.unit_list.append(new_hero)

        for hero in cur:
            new_hero = Hero(*hero)
            self.unit_list.append(new_hero)

        self.unit_names = dict()
        self.unit_names['null'] = 0
        self.unit_names['zero'] = 0

        cur.execute("""SELECT name, id FROM hero_dict;""")
        for index in cur:
            self.unit_names[index[0]] = self.unit_list[index[1]]

        for hero in self.unit_list:
            hero.link(self)
            hero.sanity_check()


        cur.execute(
            """SELECT id, identity, name, description, type, weapon_type,
            staff_exclusive, is_seal, is_refine, is_refined_variant, range,
            disp_atk, eff_infantry, eff_armor, eff_cavalry, eff_flier,
            eff_magic, eff_dragon, hp, atk, spd, def, res, cd_mod,
            special_cd, prereq1, prereq2, sp, exclusive, infantry, armor,
            cavalry, flier, r_sword, r_tome, r_breath, b_lance, b_tome,
            b_breath, g_axe, g_tome, g_breath, c_bow, c_dagger, c_staff,
            c_breath, r_bow, b_bow, g_bow, r_dagger, b_dagger, g_dagger,
            r_beast, b_beast, g_beast, c_beast, refinable, refined_version,
            refine_sp, refine_medals, refine_stones, refine_dew, refine_eff,
            refine_staff1, refine_staff2, refine_atk, refine_spd, refine_def,
            refine_res, evolves_to, evolve_medals, evolve_stones, evolve_dew,
            evolves_from, seal_badge_color, seal_great_badges,
            seal_small_badges, seal_coins, skill_rank, tier,
            fn_pre_combat, fn_on_attack, fn_on_defend, fn_post_combat,
            fn_on_assist
            FROM skills ORDER BY id ASC;"""
        )

        self.skill_list = [None,]
        for skill in cur:
            new_skill = Skill(*skill)
            self.skill_list.append(new_skill)
        self.skill_names = dict()
        cur.execute("""SELECT name, id FROM skills_dict;""")
        for index in cur:
            self.skill_names[index[0]] = self.skill_list[index[1]]

        for skill in self.skill_list[1:]:
            skill.link(self)

        cur.execute(
            """SELECT heroid, skillid, unlockRarity, defaultRarity, type,
            exclusive
            FROM skillsets
            ORDER BY heroid ASC,  unlockRarity ASC,  exclusive ASC;"""
        )
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
        con.close()

        return(self)



    @classmethod
    def initialize_emojis(cls, client):
        print('indexing skill emoijs..')
        con = sqlite3.connect("feh/emojis.db", detect_types=sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(
            """SELECT id, typeemoteid, weapontypeemoteid 
            FROM skill_emoji WHERE id > 0 ORDER BY id ASC;"""
        )
        for index in cur:
            skill = cls.singleton.skill_list[index[0]]
            skill.icon = client.get_emoji(int(index[1]))
            if index[2]:
                skill.w_icon = client.get_emoji(int(index[2]))

        cur.execute(
            """SELECT id, typeemoteid, weapontypeemoteid 
            FROM skill_emoji WHERE id < 0 ORDER BY id DESC;"""
        )
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
        return name



    @classmethod
    def get_hero(cls, hero_name):
        return copy(cls.singleton.unit_names.get(cls.filter_name(hero_name)))



    @classmethod
    def get_rhero_by_id(cls, hero_id):
        return cls.singleton.unit_list[hero_id]



    @classmethod
    def get_skill(cls, skill_name):
        return copy(cls.singleton.skill_names.get(cls.filter_name(skill_name)))



    @classmethod
    def get_rskill_by_id(cls, skill_id):
        return cls.singleton.skill_list[skill_id]



    @staticmethod
    def insert_hero_alias(hero, name):
        con = sqlite3.connect("feh/fehdata.db", detect_types=sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute('INSERT INTO hero_dict (name, id) VALUES (?, ?)',
                    (name, hero.id))
        con.commit()
        con.close()
        UnitLib.singleton.unit_names[name] = hero



    @staticmethod
    def insert_skill_alias(skill, name):
        con = sqlite3.connect("feh/fehdata.db", detect_types=sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute('INSERT INTO skills_dict (name, id) VALUES (?, ?)',
                    (name, skill.id))
        con.commit()
        con.close()
        UnitLib.singleton.unit_names[name] = skill



    @classmethod
    def get_unitlib(cls):
        if cls.singleton is None:
            cls.initialize()
        return cls.singleton
