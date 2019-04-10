import asyncio
import sqlite3
from copy import copy
from string import punctuation, whitespace

from feh.emojilib import EmojiLib as em
from feh.hero import Hero, Stat, UnitColor, UnitWeaponType, MoveType
from feh.skill import Skill, SkillType, Refine

SEARCH_SPECIAL_CHARS = '"()*'
TRANSTAB = str.maketrans('', '', punctuation + whitespace)
TRANS_SEARCH = str.maketrans(
    punctuation.translate(str.maketrans('', '', SEARCH_SPECIAL_CHARS)),
    ' ' * (len(punctuation) - len(SEARCH_SPECIAL_CHARS))
)
TRANS_SEARCH_SYNTAX = str.maketrans(
    SEARCH_SPECIAL_CHARS,' ' * len(SEARCH_SPECIAL_CHARS))


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
        con = sqlite3.connect("feh/fehdata.db")
        cur = con.cursor()
        cur.execute(
            """SELECT id, name, short_name, epithet, color,
            weapon_type, move_type, base_hp, base_atk, base_spd, base_def,
            base_res, grow_hp, grow_atk, grow_spd, grow_def, grow_res,
            max_hp, max_atk, max_spd, max_def, max_res, is_legend,
            legend_element, legend_boost, tome_type, description, bvid,
            artist, vo_en, vo_jp, alt_base_id, is_story, is_seasonal,
            is_grail, is_veteran, is_trainee, is_dancer, is_brave,
            is_sigurd, is_enemy, generation
            FROM hero ORDER BY id ASC;"""
        )
        self = UnitLib()
        cls.singleton = self
        self.unit_list = []
        new_hero = Hero(
            0, 'null', 'Null', 'Null Hero',
            UnitColor.RED, UnitWeaponType.R_SWORD, MoveType.INFANTRY,
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
        cur.execute(
            """SELECT id, name, short_name, epithet, color,
            weapon_type, move_type, base_hp, base_atk, base_spd, base_def,
            base_res, grow_hp, grow_atk, grow_spd, grow_def, grow_res,
            max_hp, max_atk, max_spd, max_def, max_res, is_legend,
            legend_element, legend_boost, tome_type, description, bvid,
            artist, vo_en, vo_jp, alt_base_id, is_story, is_seasonal,
            is_grail, is_veteran, is_trainee, is_dancer, is_brave,
            is_sigurd, is_enemy, generation
            FROM enemy ORDER BY id DESC;"""
        )
        self.enemy_list = []
        self.enemy_list.append(self.unit_list[0])
        for hero in cur:
            new_hero = Hero(*hero)
            self.enemy_list.append(new_hero)
        self.enemy_names = dict()
        self.enemy_names['null'] = 0
        for hero in self.unit_list:
            hero.link(self)
            hero.sanity_check()
        for hero in self.enemy_list:
            hero.link(self)
            hero.sanity_check()
        cur.execute(
            """SELECT id, identity, name, description, type, weapon_type,
            staff_exclusive, is_seal, is_refine, is_refined_variant, range,
            might, eff_infantry, eff_armor, eff_cavalry, eff_flier,
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
            seal_small_badges, seal_coins, skill_rank, tier
            FROM skills ORDER BY id ASC;"""
        )
        self.skill_list = [None,]
        for skill in cur:
            new_skill = Skill(*skill)
            self.skill_list.append(new_skill)
        self.skill_names = dict()
        for skill in self.skill_list[1:]:
            skill.link(self)
        for skill in self.skill_list[1:]:
            if not skill.tier: skill.set_tier_recursive()
        cur.execute(
            """SELECT heroid, skillid, unlockRarity, defaultRarity
            FROM skillsets
            ORDER BY heroid ASC,  unlockRarity ASC,  exclusive ASC;"""
        )
        for index in cur:
            hero = self.unit_list[index[0]]
            skill = self.skill_list[index[1]]
            if skill.skill_type == SkillType.WEAPON:
                hero.weapon.append((skill, index[2], index[3]))
                if skill.exclusive: hero.weapon_prf = skill
            elif skill.skill_type == SkillType.ASSIST:
                hero.assist.append((skill, index[2], index[3]))
            elif skill.skill_type == SkillType.SPECIAL:
                hero.special .append((skill, index[2], index[3]))
            elif skill.skill_type == SkillType.PASSIVE_A:
                hero.passive_a.append((skill, index[2], index[3]))
            elif skill.skill_type == SkillType.PASSIVE_B:
                hero.passive_b.append((skill, index[2], index[3]))
            elif skill.skill_type == SkillType.PASSIVE_C:
                hero.passive_c.append((skill, index[2], index[3]))
            skill.learnable[index[2]].append(hero)
            if skill.exclusive: skill.exclusive_to_id.add(index[0])
        con.close()
        con = sqlite3.connect("feh/names.db")
        cur = con.cursor()
        cur.execute("""SELECT name, id FROM heroes;""")
        for index in cur:
            self.unit_names[index[0]] = self.unit_list[index[1]]
        cur.execute("""SELECT name, id FROM enemy;""")
        for index in cur:
            self.enemy_names[index[0]] = self.enemy_list[abs(index[1])]
        cur.execute("""SELECT name, id FROM skills;""")
        for index in cur:
            self.skill_names[index[0]] = self.skill_list[index[1]]
        con.close()
        print('done.')
        return self

    @classmethod
    def initialize_emojis(cls, client):
        print('indexing skill emoijs..')
        con = sqlite3.connect("feh/emojis.db")
        cur = con.cursor()
        cur.execute(
            """SELECT id, typeemoteid
            FROM skill_emoji WHERE id > 0 ORDER BY id ASC;"""
        )
        for index in cur:
            skill = cls.singleton.skill_list[index[0]]
            skill.icon = client.get_emoji(int(index[1]))

        cur.execute(
            """SELECT id, typeemoteid
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
        return name.lower().replace('+', 'plus').translate(TRANSTAB)

    @classmethod
    def check_name(cls, hero_name):
        return cls.filter_name(hero_name) in cls.singleton.unit_names

    @classmethod
    def get_base_hero(cls, hero_name, user_id):
        hero_name = cls.filter_name(hero_name)
        if hero_name.startswith('enemy') or hero_name.endswith('enemy'):
            if hero_name.startswith('enemy'):
                hero_name = hero_name[5:]
            if hero_name.endswith('enemy'):
                hero_name = hero_name[:-5]
            if hero_name in cls.singleton.enemy_names:
                hero = copy(cls.singleton.enemy_names[hero_name])
                hero.equipped = (
                    copy(cls.singleton.enemy_names[hero_name].equipped))
                return hero
            return None
        if hero_name in cls.singleton.unit_names:
            hero = copy(cls.singleton.unit_names[hero_name])
            hero.equipped = copy(cls.singleton.unit_names[hero_name].equipped)
            return hero
        return None

    @classmethod
    def search_hero(cls, hero_name, user_id):
        hero_name = hero_name.translate(TRANS_SEARCH).lstrip('*')
        con = sqlite3.connect("feh/fehdata.db")
        cur = con.cursor()
        try:
            cur.execute(
                'SELECT id FROM hero_search WHERE hero_search MATCH ? '
                'ORDER BY RANDOM() LIMIT 2',
                (hero_name,)
            )
        except sqlite3.OperationalError:
            hero_name = hero_name.translate(TRANS_SEARCH_SYNTAX)
            try:
                cur.execute(
                    'SELECT id FROM hero_search WHERE hero_search MATCH ? '
                    'ORDER BY RANDOM() LIMIT 2',
                    (hero_name,)
                )
            except sqlite3.OperationalError:
                return None
        hero_id = cur.fetchone()
        if hero_id is not None:
            hero = copy(cls.singleton.unit_list[hero_id[0]])
            hero.equipped = copy(cls.singleton.unit_list[hero_id[0]].equipped)
            if cur.fetchone() is None:
                asyncio.create_task(
                    cls.insert_hero_alias(hero, cls.filter_name(hero_name)))
            return hero
        return None

    @classmethod
    def get_hero(cls, hero_name, user_id):
        hero = cls.get_base_hero(hero_name, user_id)
        if hero is not None:
            return hero
        hero = UnitLib.get_custom_hero(hero_name, user_id)
        if hero is not None:
            return hero
        return cls.search_hero(hero_name, user_id)

    @classmethod
    def get_rhero_by_id(cls, hero_id):
        if hero_id < 0:
            return cls.singleton.enemy_list[abs(hero_id)]
        return cls.singleton.unit_list[hero_id]

    #todo: THIS DOESNT WORK!!!
    @classmethod
    def get_skill_by_search(cls, skill_name):
        skill_name = skill_name.translate(TRANS_SEARCH).lstrip('*')
        con = sqlite3.connect("feh/fehdata.db")
        cur = con.cursor()
        cur.execute(
            'SELECT id FROM skill_search WHERE skill_search MATCH ? '
            'ORDER BY RANDOM() LIMIT 2',
            (skill_name,)
        )
        skill_id = cur.fetchone()
        if skill_id is not None:
            skill = cls.singleton.skill_list[skill_id[0]]
            if cur.fetchone() is None:
                asyncio.create_task(
                    cls.insert_skill_alias(skill, cls.filter_name(skill_name)))
            return skill
        return None
       
    @classmethod
    def get_skill(cls, skill_name):
        search_name = cls.filter_name(skill_name)
        if search_name.endswith('eff', -3):
            ref_type = Refine.EFFECT
            base_name = search_name[:-3]
        elif search_name.endswith('atk', -3):
            ref_type = Refine.ATK
            base_name = search_name[:-3]
        elif search_name.endswith('spd', -3):
            ref_type = Refine.SPD
            base_name = search_name[:-3]
        elif search_name.endswith('def', -3):
            ref_type = Refine.DEF
            base_name = search_name[:-3]
        elif search_name.endswith('res', -3):
            ref_type = Refine.RES
            base_name = search_name[:-3]
        elif search_name.endswith('wrathful', -8):
            ref_type = Refine.STAFF1
            base_name = search_name[:-8]
        elif search_name.endswith('dazzling', -8):
            ref_type = Refine.STAFF2
            base_name = search_name[:-8]
        else:
            ref_type = None
            base_name = search_name
        base_name = base_name.replace('plusplus', 'plus')
        if base_name in cls.singleton.skill_names:
            skill = cls.singleton.skill_names[base_name]
        elif base_name[:-4] in cls.singleton.skill_names:
            skill = cls.singleton.skill_names[base_name[:-4]]
        elif search_name in cls.singleton.skill_names:
            skill = cls.singleton.skill_names[search_name]
            ref_type = None
        else:
            return None
        if ref_type:
            refine = skill.get_refine(ref_type)
            if refine is None and skill.postreq: # fail case
                new_refine = skill.postreq[0].get_refine(ref_type)
                if new_refine is not None:
                    skill = skill.postreq[0]
                    refine = new_refine
            skill = skill.get_refined(refine)
        return skill

    @classmethod
    def get_rskill_by_id(cls, skill_id):
        return cls.singleton.skill_list[skill_id]

    @classmethod
    def search_skills(cls, search_str):
        con = sqlite3.connect("feh/fehdata.db")
        cur = con.cursor()
        #search_str = f'"{search_str}"'
        search_str = (search_str.replace('&', ' AND ').replace('|', ' OR ')
                      .replace('-', ' NOT '))
        search_str = search_str.translate(TRANS_SEARCH).lstrip('*')
        try:
            cur.execute(
                'SELECT id, identity, '
                'snippet(skill_search, -1, "**", "**", "…", 10)'
                'FROM skill_search '
                'WHERE skill_search MATCH ? ORDER BY rank ASC;',
                (search_str,)
            )
        except sqlite3.OperationalError:
            #EAFP
            search_str = search_str.translate(TRANS_SEARCH_SYNTAX)
            try:
                cur.execute(
                    'SELECT id, identity, '
                    'snippet(skill_search, -1, "**", "**", "…", 10)'
                    'FROM skill_search '
                    'WHERE skill_search MATCH ? ORDER BY rank ASC;',
                    (search_str,)
                )
            except sqlite3.OperationalError:
                return None
        skill_list = [
            (cls.singleton.skill_list[int(result[0])].icon,
             result[1], result[2])
            for result in cur
        ]
        con.close()
        return skill_list

    @classmethod
    async def insert_hero_alias(cls, hero, name):
        if name in cls.singleton.unit_names:
            return False
        con = sqlite3.connect("feh/names.db")
        cur = con.cursor()
        if hero.index > 0:
            cur.execute('INSERT INTO heroes (name, id) VALUES (?, ?);',
                        (name, hero.index))
            cls.singleton.unit_names[name] = hero
        else:
            cur.execute('INSERT INTO enemy (name, id) VALUES (?, ?);',
                        (name, hero.index))
            cls.singleton.enemy_names[name] = hero
        con.commit()
        con.close()
        return True

    @classmethod
    def insert_skill_alias(cls, skill, name):
        if name in cls.singleton.skill_names: return False
        con = sqlite3.connect("feh/names.db")
        cur = con.cursor()
        cur.execute('INSERT INTO skills (name, id) VALUES (?, ?);',
                    (name, skill.index))
        con.commit()
        con.close()
        cls.singleton.skill_names[name] = skill
        return True

    @classmethod
    def insert_custom_hero(cls, hero, user_id):
        search_name = cls.filter_name(hero.custom_name)
        if search_name in cls.singleton.unit_names:
            return 1
        con = sqlite3.connect("feh/userdata.db")
        cur = con.cursor()
        cur.execute('SELECT COUNT(*) FROM user_heroes WHERE user_id = ?',
                    (user_id,))
        count = cur.fetchone()
        if count[0] > 300:
            con.close()
            return 2
        cur.execute('SELECT COUNT(*) FROM user_heroes WHERE search_name = ? '
                    'AND user_id = ?', (search_name, user_id))
        count = cur.fetchone()
        if count[0] > 0:
            con.close()
            return 3
        cur.execute(
            'INSERT INTO user_heroes (user_id, search_name, hero_id, name, '
            'asset, flaw, rarity, merges, dragonflowers, summ_support, '
            'weapon_id, assist_id, special_id, passive_a_id, passive_b_id, '
            'passive_c_id, passive_s_id, refine_id) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
            (
                user_id, search_name, hero.index, hero.custom_name,
                hero.boon.value, hero.bane.value, hero.rarity, hero.merges,
                hero.flowers, hero.summ_support,
                hero.equipped.weapon.index if hero.equipped.weapon else 0,
                hero.equipped.assist.index if hero.equipped.assist else 0,
                hero.equipped.special.index if hero.equipped.special else 0,
                hero.equipped.passive_a.index
                if hero.equipped.passive_a else 0,
                hero.equipped.passive_b.index
                if hero.equipped.passive_b else 0,
                hero.equipped.passive_c.index
                if hero.equipped.passive_c else 0,
                hero.equipped.passive_s.index
                if hero.equipped.passive_s else 0,
                hero.equipped.weapon.refine_path.index
                if hero.equipped.weapon and hero.equipped.weapon.refine_path
                else 0,
            )
        )
        con.commit()
        con.close()
        return 0

    @classmethod
    def get_custom_heroes_names(cls, search_names, user_id):
        con = sqlite3.connect("feh/userdata.db")
        cur = con.cursor()
        query = (
            'SELECT name FROM user_heroes WHERE user_id = ? '
            'AND (search_name = ?'
            f'{" OR search_name = ?" * (len(search_names) - 1)})'
        )
        cur.execute(
            query,(user_id, *[cls.filter_name(name) for name in search_names]))
        result = [row[0] for row in cur]
        con.close()
        return result

    @classmethod
    def get_custom_hero(cls, hero_name, user_id):
        search_name = cls.filter_name(hero_name)
        con = sqlite3.connect("feh/userdata.db")
        cur = con.cursor()
        cur.execute(
            'SELECT hero_id, name, asset, flaw, merges, rarity, '
            'dragonflowers, summ_support, weapon_id, assist_id, special_id, '
            'passive_a_id, passive_b_id, passive_c_id, passive_s_id, '
            'refine_id FROM user_heroes WHERE user_id = ? '
            'AND search_name = ?',
            (user_id, search_name)
        )
        hero_data = cur.fetchone()
        con.close()
        if not hero_data:
            return None
        if hero_data[0] >= 0:
            hero = copy(cls.singleton.unit_list[hero_data[0]])
        else:
            hero = copy(cls.singleton.enemy_list[abs(hero_data[0])])
        hero.equipped = copy(cls.singleton.unit_list[hero_data[0]].equipped)
        hero.custom_name = hero_data[1]
        hero.update_stat_mods(
            boon=Stat(hero_data[2]),
            bane=Stat(hero_data[3]),
            merges=hero_data[4],
            rarity=hero_data[5],
            flowers=hero_data[6],
            summ_support=hero_data[7],
        )
        hero.equipped.weapon = cls.singleton.skill_list[hero_data[8]]
        hero.equipped.assist = cls.singleton.skill_list[hero_data[9]]
        hero.equipped.special = cls.singleton.skill_list[hero_data[10]]
        hero.equipped.passive_a = cls.singleton.skill_list[hero_data[11]]
        hero.equipped.passive_b = cls.singleton.skill_list[hero_data[12]]
        hero.equipped.passive_c = cls.singleton.skill_list[hero_data[13]]
        hero.equipped.passive_s = cls.singleton.skill_list[hero_data[14]]
        if hero_data[8] and hero_data[15]:
            hero.equipped.weapon = hero.equipped.weapon.get_refined(
                cls.singleton.skill_list[hero_data[15]])
        return hero

    @classmethod
    def list_custom_heroes(cls, user_id):
        con = sqlite3.connect("feh/userdata.db")
        cur = con.cursor()
        cur.execute(
            'SELECT hero_id, name FROM user_heroes WHERE user_id = ?;',
            (user_id,)
        )
        hero_list = [
            f'{em.get(cls.singleton.unit_list[row[0]].weapon_type)}'
            f'{em.get(cls.singleton.unit_list[row[0]].move_type)} '
            f'{row[1]} [{cls.singleton.unit_list[row[0]].short_name}]'
            for row in cur
        ]
        con.close()
        return hero_list

    @classmethod
    def update_custom_hero(cls, hero, user_id):
        search_name = cls.filter_name(hero.custom_name)
        con = sqlite3.connect("feh/userdata.db")
        cur = con.cursor()
        cur.execute('SELECT COUNT(*) FROM user_heroes WHERE search_name = ? '
                    'AND user_id = ?', (search_name, user_id))
        count = cur.fetchone()
        if count[0] != 1:
            con.close()
            return False
        cur.execute(
            'UPDATE user_heroes SET hero_id = ?, asset = ?, flaw = ?, '
            'rarity = ?, merges = ?, dragonflowers = ?, summ_support = ?, '
            'weapon_id = ?,  assist_id = ?, special_id = ?, passive_a_id = ?, '
            'passive_b_id = ?, passive_c_id = ?, passive_s_id = ?, '
            'refine_id = ? WHERE user_id = ? AND search_name = ?;',
            (
                hero.index, hero.boon.value, hero.bane.value, hero.rarity, 
                hero.merges, hero.flowers, hero.summ_support,
                hero.equipped.weapon.index if hero.equipped.weapon else 0,
                hero.equipped.assist.index if hero.equipped.assist else 0,
                hero.equipped.special.index if hero.equipped.special else 0,
                hero.equipped.passive_a.index
                if hero.equipped.passive_a else 0,
                hero.equipped.passive_b.index
                if hero.equipped.passive_b else 0,
                hero.equipped.passive_c.index
                if hero.equipped.passive_c else 0,
                hero.equipped.passive_s.index
                if hero.equipped.passive_s else 0,
                hero.equipped.weapon.refine_path.index
                if hero.equipped.weapon and hero.equipped.weapon.refine_path
                else 0,
                user_id, search_name, 
            )
        )
        con.commit()
        con.close()
        return True

    @classmethod
    def rename_custom_hero(cls, old_name, new_name, user_id):
        old_search_name = cls.filter_name(old_name)
        new_search_name = cls.filter_name(new_name)
        if new_search_name in cls.singleton.unit_names:
            return 1, None
        con = sqlite3.connect("feh/userdata.db")
        cur = con.cursor()
        cur.execute('SELECT name FROM user_heroes WHERE search_name = ? '
                    'AND user_id = ?', (old_search_name, user_id))
        name = cur.fetchone()
        if name is None:
            con.close()
            return 2, None
        cur.execute('SELECT COUNT(*) FROM user_heroes WHERE search_name = ? '
                    'AND user_id = ?', (new_search_name, user_id))
        count = cur.fetchone()
        if count[0] > 0 and old_search_name != new_search_name:
            con.close()
            return 3, None
        cur.execute(
            'UPDATE user_heroes SET search_name = ?, name = ? '
            'WHERE user_id = ? AND search_name = ?',
            (new_search_name, new_name, user_id, old_search_name)
        )
        con.commit()
        con.close()
        return 0, name[0]

    @classmethod
    def delete_custom_heroes(cls, hero_names, user_id):
        con = sqlite3.connect("feh/userdata.db")
        cur = con.cursor()
        query = (
            'DELETE FROM user_heroes WHERE user_id = ? AND (search_name = ?'
            f'{" OR search_name = ?" * (len(hero_names) - 1)})'
        )
        cur.execute(
            query, (user_id, *[cls.filter_name(name) for name in hero_names]))
        con.commit()
        con.close()

    @classmethod
    def get_unitlib(cls):
        if cls.singleton is None:
            cls.initialize()
        return cls.singleton
