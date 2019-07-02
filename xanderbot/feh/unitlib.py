import asyncio
import math
import re
import sqlite3
from copy import copy
from string import punctuation, whitespace

import command.common
from feh.emojilib import EmojiLib as em
from feh.hero import Hero, Stat, UnitColor, UnitWeaponType, MoveType
from feh.skill import Skill, SkillType, Refine

ALPHA_CHARS = re.compile(r'[a-z]')
SORT_FLOAT = re.compile(r'[/\.](?=[0-9])')
BOTTOM_SYNONYMS = re.compile(
    r'\s*(?:bot(?:tom)?|lowest|worst|least|fewest|ascending|up|low|small'
    r'|little)\s*'
)
FULL_SHORTNAMES = re.compile(r'^[cwmasdrh]+$')
TOP_SYNONYMS = re.compile(
    r'\s*(?:top|highest|best|most|greatest|descending|down|high|big)\s*')
STAT_NAMES_R = (
    r'\bh(?:p|it(?:points?)?)?\b'
    r'|\ba(?:t(?:k|tack))?\b'
    r'|\bs(?:p(?:d|eed))?\b'
    r'|\bd(?:ef(?:en[cs]e)?)?\b'
    r'|\br(?:es(?:istance)?)?\b'
)
COLOR_R = r'\bc(?:olou?r)?\b'
WEAPON_R = r'\bw(?:e(?:p|apon))?(?:type)?\b'
MOVE_R = r'\bm(?:ove(?:ment)?)?(?:type)?\b'
SORT_ALLOWED = re.compile('|'.join((
    STAT_NAMES_R, COLOR_R, WEAPON_R, MOVE_R,
    r'[+\-](?=[\w(])|(?<=[\w)])[*/](?=[\w(])|[0-9]*\.?[0-9]+|[()]',
)))
STAT_NAMES = re.compile(STAT_NAMES_R)
COLOR_LIT = re.compile(COLOR_R)
WEAPON_LIT = re.compile(WEAPON_R)
MOVE_LIT = re.compile(MOVE_R)
SEARCH_SPECIAL_CHARS = '"&\'()*-|,'
ONLY_ALPHANUM = str.maketrans('', '', whitespace + punctuation)
PUNCT_NON_SEARCH_STR = punctuation.translate(
    str.maketrans('', '', SEARCH_SPECIAL_CHARS))
PUNCT_NON_SEARCH = str.maketrans(
    PUNCT_NON_SEARCH_STR, ' ' * len(PUNCT_NON_SEARCH_STR))
PARENTHETICAL = re.compile(r'\(.*\)')
REMOVE_SEARCH_SPECIAL = str.maketrans(
    SEARCH_SPECIAL_CHARS, ' ' * len(SEARCH_SPECIAL_CHARS))
REMOVE_PUNCT = str.maketrans('', '', punctuation)
REMOVE_WSPACE = str.maketrans('', '', whitespace)
LSTRIP_SEARCH = whitespace + '*&|)'
RSTRIP_SEARCH = whitespace + '-&|('
HAS_DIGIT = re.compile(r'\d')


class DummyHero(Hero):

    __slots__ = ('equip_list_all')

    def __init__(
            self, index, name, short_name, epithet, color,
            weapon_type, move_type,
            base_hp, base_atk, base_spd, base_def, base_res,
            grow_hp, grow_atk, grow_spd, grow_def, grow_res,
            max_hp, max_atk, max_spd, max_def, max_res,
    ):
        super().__init__(
            index, name, short_name, epithet, color,
            weapon_type, move_type,
            base_hp, base_atk, base_spd, base_def, base_res,
            grow_hp, grow_atk, grow_spd, grow_def, grow_res,
            max_hp, max_atk, max_spd, max_def, max_res,
        )
        self.equip_list_all = []

    def equip(self, skill, *, force_seal=False, fail_fast=False,
              keyword_mode=False, max_rarity=5):
        if force_seal:
            skill = copy(skill)
            skill.skill_type = SkillType.PASSIVE_SEAL
        self.equip_list_all.append(skill)
        return True


DUMMY_HERO = DummyHero(
    0, 'null', 'Null', 'Null Hero',
    UnitColor.RED, UnitWeaponType.R_SWORD, MoveType.INFANTRY,
    15, 8, 8, 8, 8,
    55, 50, 50, 50, 50,
    39, 30, 30, 30, 30,
)


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
            15, 8, 8, 8, 8,
            55, 50, 50, 50, 50,
            39, 30, 30, 30, 30,
        )
        self.unit_list.append(new_hero)
        for hero in cur:
            new_hero = Hero(*hero)
            self.unit_list.append(new_hero)
        self.unit_names = dict()
        self.unit_names['null'] = self.unit_list[0]
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
        self.enemy_names['null'] = self.enemy_list[0]
        for hero in self.unit_list:
            hero.link(self)
            hero.sanity_check()
        for hero in self.enemy_list:
            hero.link(self)
            hero.sanity_check()
        cur.execute(
            """SELECT id, identity, name, description, type, weapon_type,
            staff_exclusive, is_seal, is_refine, is_refined_variant, range,
            might, hp, atk, spd, def, res, cd_mod, special_cd, prereq1,
            prereq2, sp, exclusive, eff_infantry, eff_armor, eff_cavalry,
            eff_flier, eff_r_sword, eff_b_lance, eff_g_axe, eff_r_bow,
            eff_b_bow, eff_g_bow, eff_c_bow, eff_r_dagger, eff_b_dagger,
            eff_g_dagger, eff_c_dagger, eff_r_tome, eff_b_tome, eff_g_tome,
            eff_c_staff, eff_r_breath, eff_b_breath, eff_g_breath,
            eff_c_breath, eff_r_beast, eff_b_beast, eff_g_beast, eff_c_beast,
            infantry, armor, cavalry, flier, r_sword, b_lance, g_axe, r_bow,
            b_bow, g_bow, c_bow, r_dagger, b_dagger, g_dagger, c_dagger,
            r_tome, b_tome, g_tome, c_staff, r_breath, b_breath, g_breath,
            c_breath, r_beast, b_beast, g_beast, c_beast, refinable,
            refined_version, refine_sp, refine_medals, refine_stones,
            refine_dew, refine_eff, refine_staff1, refine_staff2, refine_atk,
            refine_spd, refine_def, refine_res, evolves_to, evolve_medals,
            evolve_stones, evolve_dew, evolves_from, seal_badge_color,
            seal_great_badges, seal_small_badges, seal_coins, skill_rank,
            tier, duel_bst
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
            if not skill.tier:
                skill.set_tier_recursive()
        cur.execute(
            """SELECT skillsets.heroid, skillsets.skillid,
            skillsets.unlockRarity, skillsets.defaultRarity
            FROM skillsets
            JOIN skills ON skillsets.skillid = skills.id
            ORDER BY skillsets.heroid ASC,  skillsets.unlockRarity ASC,
            skills.exclusive ASC;"""
        )
        for index in cur:
            hero = self.unit_list[index[0]]
            skill = self.skill_list[index[1]]
            if skill.skill_type == SkillType.WEAPON:
                hero.weapon.append((skill, index[2], index[3]))
                if skill.evolves_to is not None:
                    if skill.exclusive:
                        hero.weapon.append((skill.evolves_to, 12, None))
                    else:
                        hero.weapon.append((skill.evolves_to, 11, None))
                if skill.exclusive:
                    hero.weapon_prf = skill
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
            if skill.exclusive:
                # these ids are only used for valid hero build checks
                skill.exclusive_to_id.add(index[0])
                if skill.evolves_to:
                    skill.evolves_to.exclusive_to_id.add(index[0])
        cur.execute(
            """SELECT enemy_skillsets.heroid, enemy_skillsets.skillid,
            enemy_skillsets.unlockRarity, enemy_skillsets.defaultRarity
            FROM enemy_skillsets
            JOIN skills ON enemy_skillsets.skillid = skills.id
            ORDER BY enemy_skillsets.heroid ASC,
            enemy_skillsets.unlockRarity ASC, skills.exclusive ASC;"""
        )
        for index in cur:
            hero = self.enemy_list[abs(index[0])]
            skill = self.skill_list[index[1]]
            if skill.skill_type == SkillType.WEAPON:
                hero.weapon.append((skill, index[2], index[3]))
                if skill.evolves_to is not None:
                    if skill.exclusive:
                        hero.weapon.append((skill.evolves_to, 12, None))
                    else:
                        hero.weapon.append((skill.evolves_to, 11, None))
                if skill.exclusive:
                    hero.weapon_prf = skill
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
            if skill.exclusive:
                # these ids are only used for valid hero build checks
                skill.exclusive_to_id.add(index[0])
                if skill.evolves_to:
                    skill.evolves_to.exclusive_to_id.add(index[0])
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
        self.unit_list[0].equip(self.skill_list[4])
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
            skill.icon = client.get_emoji(index[1])
        cur.execute(
            """SELECT id, typeemoteid
            FROM skill_emoji WHERE id < 0 ORDER BY id DESC;"""
        )
        empty_slots = cur.fetchall()
        Skill.EMPTY_WEAPON .icon = client.get_emoji(empty_slots[0][1])
        Skill.EMPTY_ASSIST .icon = client.get_emoji(empty_slots[1][1])
        Skill.EMPTY_SPECIAL.icon = client.get_emoji(empty_slots[2][1])
        Skill.EMPTY_PASSIVE_A.icon = client.get_emoji(empty_slots[3][1])
        Skill.EMPTY_PASSIVE_B.icon = client.get_emoji(empty_slots[4][1])
        Skill.EMPTY_PASSIVE_C.icon = client.get_emoji(empty_slots[5][1])
        Skill.EMPTY_PASSIVE_S.icon = client.get_emoji(empty_slots[6][1])
        print('done.')

    @staticmethod
    def filter_name(name):
        return (
            name.lower().replace('+', 'plus').translate(ONLY_ALPHANUM).strip()
        )

    @staticmethod
    def filter_search(name):
        name = (
            name.translate(PUNCT_NON_SEARCH).lstrip(LSTRIP_SEARCH)
            .rstrip(RSTRIP_SEARCH).replace('&', ' AND ').replace('|', ' OR ')
            .replace(',', ' OR ').replace('-', ' NOT ')
        )
        if name.startswith(' NOT'):
            return 'any' + name
        return name

    @classmethod
    def check_name(cls, hero_name):
        return cls.filter_name(hero_name) in cls.singleton.unit_names

    @classmethod
    def get_base_hero(cls, hero_name, user_id):
        hero_name = cls.filter_name(hero_name)
        enemy_name = None
        if hero_name.startswith('enemy'):
            enemy_name = hero_name[5:].strip()
        elif hero_name.endswith('enemy'):
            enemy_name = hero_name[:-5].strip()
        if enemy_name is not None and enemy_name in cls.singleton.enemy_names:
            hero = copy(cls.singleton.enemy_names[enemy_name])
            hero.equipped = copy(hero.equipped)
            return hero
        if hero_name in cls.singleton.unit_names:
            hero = copy(cls.singleton.unit_names[hero_name])
            hero.equipped = copy(hero.equipped)
            return hero
        return None

    @classmethod
    def search_hero(cls, hero_name, user_id):
        hero_name = cls.filter_search(hero_name)
        con = sqlite3.connect("feh/fehdata.db")
        cur = con.cursor()
        try:
            cur.execute(
                'SELECT id FROM hero_search WHERE hero_search MATCH ? '
                'ORDER BY RANDOM() LIMIT 2',
                (hero_name,)
            )
        except sqlite3.OperationalError:
            hero_name = hero_name.translate(REMOVE_SEARCH_SPECIAL)
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
            hero.equipped = copy(hero.equipped)
            if cur.fetchone() is None:
                asyncio.create_task(
                    cls.insert_hero_alias(
                        cls.singleton.unit_list[hero_id[0]],
                        cls.filter_name(hero_name))
                    )
            con.close()
            return hero
        con.close()
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

    @classmethod
    def sort_heroes(cls, sort_terms, search_terms, equip_terms, user_id):
        sort_exprs = []
        for expr in sort_terms:
            test = TOP_SYNONYMS.subn('', expr, count=1)
            if test[1] == 1 and test[0]:
                if FULL_SHORTNAMES.fullmatch(test[0]):
                    for char in test[0]:
                        sort_exprs.append((char, 1))
                else:
                    sort_exprs.append(test)
                continue
            test = BOTTOM_SYNONYMS.subn('', expr, count=1)
            if test[1] == 1 and test[0]:
                if FULL_SHORTNAMES.fullmatch(test[0]):
                    for char in test[0]:
                        sort_exprs.append((char, 1))
                else:
                    sort_exprs.append((test[0], 0))
            elif FULL_SHORTNAMES.fullmatch(expr):
                for char in expr:
                    sort_exprs.append((char, 1))
            elif expr:
                sort_exprs.append((expr, 1))
        if search_terms:
            match = 'WHERE hero_search MATCH ? '
            search_terms = cls.filter_search(search_terms)
            parameterized = (search_terms,)
        else:
            match = ''
            parameterized = ()
        if equip_terms:
            filtered_cache_terms = []
        filtered_terms = ['hero.id, hero.short_name']
        filtered_order = []
        filtered_disp = []
        filtered_short = []
        prec = []
        padding = []
        con = sqlite3.connect("feh/fehdata.db")
        cur = con.cursor()
        if any(sort_exprs):
            for expr in sort_exprs:
                pre_filtered = ''.join(SORT_ALLOWED.findall(
                        expr[0].lower().translate(REMOVE_WSPACE)))
                if COLOR_LIT.search(pre_filtered):
                    if equip_terms:
                        filtered_order.append(
                            f'{"" if expr[1] else "-"}hero.color')
                    else:
                        filtered_order.append(
                            f'hero.color {"ASC" if expr[1] else "DESC"}')
                    filtered_disp.append('Color')
                    continue
                if WEAPON_LIT.search(pre_filtered):
                    if equip_terms:
                        filtered_order.append(
                            f'{"" if expr[1] else "-"}hero.weapon_type')
                    else:
                        filtered_order.append(
                            f'hero.weapon_type {"ASC" if expr[1] else "DESC"}')
                    filtered_disp.append('Weapon')
                    continue
                if MOVE_LIT.search(pre_filtered):
                    if equip_terms:
                        filtered_order.append(
                            f'{"" if expr[1] else "-"}hero.move_type')
                    else:
                        filtered_order.append(
                            f'hero.move_type {"ASC" if expr[1] else "DESC"}')
                    filtered_disp.append('Move')
                    continue
                filtered_term = (
                    STAT_NAMES.sub(
                        lambda match:
                            Stat.get_by_name(match.group()).db_col,
                        pre_filtered
                    )
                    .replace('/', '*1.0/')
                )
                if filtered_term:
                    filtered_terms.append(filtered_term)
                    if equip_terms:
                        filtered_cache_terms.append(STAT_NAMES.sub(
                            lambda match:
                                Stat.get_by_name(match.group()).hero_final,
                            pre_filtered
                        ).replace('*', '\*')
                    )
                    filtered_disp.append(STAT_NAMES.sub(
                            lambda match:
                                Stat.get_by_name(match.group()).short,
                            pre_filtered
                        ).replace('*', '\*')
                    )
                    filtered_short.append(STAT_NAMES.sub(
                        lambda match: match.group()[0], pre_filtered)
                    )
                    if SORT_FLOAT.search(filtered_term):
                        prec.append(1)
                    else:
                        prec.append(0)
                    if ALPHA_CHARS.search(filtered_term):
                        try:
                            cur.execute(
                                f'SELECT ABS({filtered_term}) '
                                'FROM hero_search '
                                'JOIN hero ON hero_search.id = hero.id '
                                f'{match}'
                                f'ORDER BY ABS({filtered_term}) DESC '
                                'LIMIT 1',
                                parameterized
                            )
                        except sqlite3.OperationalError:
                            con.close()
                            return None, '', ()
                        if equip_terms:
                            filtered_order.append(
                                f'{"-" if expr[1] else ""}'
                                f'({filtered_cache_terms[-1]})'
                            )
                        else:
                            filtered_order.append(
                                f'{filtered_term} '
                                f'{"DESC" if expr[1] else "ASC"}'
                            )
                        max_val = cur.fetchone()
                        if max_val is None:
                            con.close()
                            return (), '', ()
                        max_val = max_val[0]
                        try:
                            cur.execute(
                                'SELECT CASE '
                                f'WHEN {filtered_term} < 0 THEN 1 ELSE 0 '
                                'END negative '
                                'FROM hero_search '
                                'JOIN hero ON hero_search.id = hero.id '
                                f'{match}'
                                f'ORDER BY {filtered_term} ASC '
                                'LIMIT 1',
                                parameterized
                            )
                        except sqlite3.OperationalError:
                            con.close()
                            return None, '', ()
                        negative = cur.fetchone()[0]
                        if max_val is not None and max_val != 0:
                            padding.append(int(math.log10(max_val))
                                           + 1 + 2 * prec[-1] + negative)
                        else:
                            padding.append(0)
                    else:
                        padding.append(0)
        if equip_terms:
            filtered_order.append('hero.index')
        else:
            filtered_order.append('hero.id ASC')
        if not equip_terms or not filtered_short:
            try:
                cur.execute(
                    f'SELECT {", ".join(filtered_terms)} '
                    'FROM hero_search JOIN hero ON hero_search.id = hero.id '
                    f'{match}'
                    f'ORDER BY {", ".join(filtered_order)}',
                    parameterized
                )
            except sqlite3.OperationalError:
                con.close()
                return None, '', ()
            if len(filtered_short) == 0:
                hero_list = [(
                        f'{em.get(cls.singleton.unit_list[rw[0]].weapon_type)}'
                        f'{em.get(cls.singleton.unit_list[rw[0]].move_type)} '
                        f'{rw[1]}'
                    )
                    for rw in cur
                ]
            elif len(filtered_short) == 1:
                hero_list = [(
                        f'``({rw[2] or 0:·>{padding[0]}.{prec[0]}f})`` '
                        f'{em.get(cls.singleton.unit_list[rw[0]].weapon_type)}'
                        f'{em.get(cls.singleton.unit_list[rw[0]].move_type)} '
                        f'{rw[1]}'
                    )
                    for rw in cur
                ]
            else:
                hero_list = [(
                        f'''``{" | ".join([
                            f"{filtered_short[cou]}="
                            f"{rw[cou+2] or 0:·>{padding[cou]}.{prec[cou]}f}"
                            for cou in range(len(filtered_short))
                        ])}`` '''
                        f'{em.get(cls.singleton.unit_list[rw[0]].weapon_type)}'
                        f'{em.get(cls.singleton.unit_list[rw[0]].move_type)} '
                        f'{rw[1]}'
                    )
                    for rw in cur
                ]
            bad_args = []
        else:
            eq_tokens = PARENTHETICAL.sub(
                lambda match: match.group().replace(',', TEMP_SEP), equip_terms)
            hero_args = eq_tokens.split(',')
            dummy_hero = copy(DUMMY_HERO)
            dummy_hero.equip_list_all = copy(dummy_hero.equip_list_all)
            dummy_hero, bad_args, not_allowed = (
                command.common.process_hero_args(
                    dummy_hero, hero_args, user_id))
            if bad_args and len(hero_args) == 1:
                dummy_hero, bad_args, not_allowed = (
                    command.common.process_hero_args(
                        dummy_hero, hero_args[0].split(), user_id))
            try:
                cur.execute(
                    f'SELECT hero.id '
                    'FROM hero_search JOIN hero ON hero_search.id = hero.id '
                    f'{match}',
                    parameterized
                )
            except sqlite3.OperationalError:
                con.close()
                return None, '', ()
            heroes = [copy(cls.singleton.unit_list[row[0]]) for row in cur]
            sort_dummy = f'({", ".join(filtered_order)})'.replace('\*', '*')
            sort_values = (
                f'({", ".join(filtered_cache_terms)})'.replace('\*', '*'))
            for hero in heroes:
                hero.equipped = copy(hero.equipped)
                for skill in dummy_hero.equip_list_all:
                    hero.equip(skill, fail_fast=True, keyword_mode=True)
                    hero.update_stat_mods(
                        boon=dummy_hero.boon, bane=dummy_hero.bane,
                        merges=dummy_hero.merges, rarity=dummy_hero.rarity,
                        flowers=dummy_hero.flowers,
                        summ_support=dummy_hero.summ_support
                    )
                hero.sort_dummy = eval(
                    sort_dummy, {'__builtins__': None}, {'hero': hero})
                hero.sort_values = eval(
                    sort_values, {'__builtins__': None}, {'hero': hero})
            heroes.sort(key=lambda hero: hero.sort_dummy)
            if len(filtered_short) == 0:
                hero_list = [(
                        f'{em.get(hero.weapon_type)}{em.get(hero.move_type)} '
                        f'{hero.short_name}'
                    )
                    for hero in heroes
                ]
            elif len(filtered_short) == 1:
                hero_list = [(
                        '``('
                        f'{hero.sort_values or 0:·>{padding[0]}.{prec[0]}f}'
                        ')`` '
                        f'{em.get(hero.weapon_type)}{em.get(hero.move_type)} '
                        f'{hero.short_name}'
                    )
                    for hero in heroes
                ]
            else:
                hero_list = [(
                        f'''``{" | ".join([
                            f"{filtered_short[cou]}="
                            f"""{hero.sort_values[cou] or 0
                            :·>{padding[cou]}.{prec[cou]}f}"""
                            for cou in range(len(filtered_short))
                        ])}`` '''
                        f'{em.get(hero.weapon_type)}{em.get(hero.move_type)} '
                        f'{hero.short_name}'
                    )
                    for hero in heroes
                ]
        con.close()
        return hero_list, ', '.join(filtered_disp), bad_args

    @classmethod
    async def log_skill_search(cls, skill_name):
        con = sqlite3.connect("feh/fehdata.db")
        cur = con.cursor()
        try:
            cur.execute(
                'INSERT OR IGNORE INTO skill_search_log (search_str) '
                'VALUES (?)', (skill_name,)
            )
        except sqlite3.OperationalError:
            pass
        else:
            con.commit()
        finally:
            con.close()

    @classmethod
    def get_skill_by_search(cls, skill_name):
        skill_name = cls.filter_search(skill_name.replace('+', ' plus '))
        if 'random' in skill_name:
            order_by = 'RANDOM()'
            logging = False
        else:
            order_by = (
                'LENGTH(skill_search.tags) '
                '+ LENGTH(skill_search.search_name) ASC, '
                'skills.skill_rank DESC, skill_search.id ASC')
            logging = True
        if HAS_DIGIT.search(skill_name):
            num_results = 2
        else:
            num_results = 4
        con = sqlite3.connect("feh/fehdata.db")
        cur = con.cursor()
        try:
            cur.execute(
                'SELECT skill_search.id FROM skill_search '
                'LEFT JOIN skills ON skill_search.id = skills.id '
                'WHERE skill_search MATCH ? '
                'AND skill_search.is_real_skill = 1 '
                f'ORDER BY {order_by} LIMIT {num_results}',
                (f'{{id search_name tags random}} : ({skill_name})',)
            )
        except sqlite3.OperationalError:
            skill_name = skill_name.translate(REMOVE_SEARCH_SPECIAL)
            try:
                cur.execute(
                    'SELECT skill_search.id FROM skill_search '
                    'LEFT JOIN skills ON skill_search.id = skills.id '
                    'WHERE skill_search MATCH ? '
                    'AND skill_search.is_real_skill = 1 '
                    f'ORDER BY {order_by} LIMIT {num_results}',
                    (f'{{id search_name tags random}} : ({skill_name})',)
                )
            except sqlite3.OperationalError:
                con.close()
                return None
        skill_id = cur.fetchone()
        if skill_id is None:
            try:
                cur.execute(
                    'SELECT skill_search.id FROM skill_search '
                    'LEFT JOIN skills ON skill_search.id = skills.id '
                    'WHERE skill_search MATCH ? '
                    'AND skill_search.is_real_skill = 1 '
                    f'ORDER BY {order_by} LIMIT {num_results}',
                    ('{id search_name type exclusive tags wielder random} : '
                     f'({skill_name})',)
                )
            except sqlite3.OperationalError:
                skill_name = skill_name.translate(REMOVE_SEARCH_SPECIAL)
                try:
                    cur.execute(
                        'SELECT skill_search.id FROM skill_search '
                        'LEFT JOIN skills ON skill_search.id = skills.id '
                        'WHERE skill_search MATCH ? '
                        'AND skill_search.is_real_skill = 1 '
                        f'ORDER BY {order_by} LIMIT {num_results}',
                        ('{id search_name type exclusive tags wielder '
                         'random} : '
                         f'({skill_name})',)
                    )
                except sqlite3.OperationalError:
                    con.close()
                    return None
            skill_id = cur.fetchone()
        if skill_id is not None:
            skill = cls.singleton.skill_list[skill_id[0]]
            if len(cur.fetchall()) < num_results - 1:
                asyncio.create_task(
                    cls.insert_skill_alias(
                        cls.singleton.skill_list[skill_id[0]],
                        cls.filter_name(skill_name))
                    )
            elif logging:
                asyncio.create_task(cls.log_skill_search(skill_name))
            con.close()
            return skill
        con.close()
        return None

    @classmethod
    def get_base_skill(cls, skill_name):
        if skill_name in cls.singleton.skill_names:
            return cls.singleton.skill_names[skill_name]
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
        elif (base_name.endswith('plus')
                and base_name[:-4] in cls.singleton.skill_names):
            skill = cls.singleton.skill_names[base_name[:-4]]
        elif search_name in cls.singleton.skill_names:
            skill = cls.singleton.skill_names[search_name]
            ref_type = None
        else:
            return cls.get_skill_by_search(skill_name)
        if ref_type:
            refine = skill.get_refine(ref_type)
            if refine is None and skill.postreq: # fail case
                new_refine = skill.postreq[0].get_refine(ref_type)
                if new_refine is not None:
                    skill = skill.postreq[0]
                    refine = new_refine
            if refine is None:
                if search_name in cls.singleton.skill_names:
                    return cls.singleton.skill_names[search_name]
                elif (search_name.endswith('plus')
                        and search_name[:-4] in cls.singleton.skill_names):
                    return cls.singleton.skill_names[search_name[:-4]]
                else:
                    return cls.get_skill_by_search(skill_name)
            else:
                skill = skill.get_refined(refine)
        return skill

    @classmethod
    def get_rskill_by_id(cls, skill_id):
        return cls.singleton.skill_list[skill_id]

    @classmethod
    def search_skills(cls, search_str):
        con = sqlite3.connect("feh/fehdata.db")
        cur = con.cursor()
        # remember this is still faster than regex
        search_str = cls.filter_search(search_str)
        try:
            cur.execute(
                'SELECT icon_id, identity, '
                'snippet(skill_search, -1, "**", "**", "…", 10) '
                'FROM skill_search '
                'WHERE skill_search MATCH ? AND search_relevant = 1 '
                'ORDER BY rank ASC;',
                ('{identity description type exclusive tags wielder} : '
                 f'({search_str})',)
            )
        except sqlite3.OperationalError:
            #EAFP
            search_str = search_str.translate(REMOVE_SEARCH_SPECIAL)
            try:
                cur.execute(
                    'SELECT icon_id, identity, '
                    'snippet(skill_search, -1, "**", "**", "…", 10) '
                    'FROM skill_search '
                    'WHERE skill_search MATCH ? '
                    'AND search_relevant = 1 ORDER BY rank ASC;',
                    ('{identity description type exclusive tags wielder} : '
                     f'({search_str})',)
                )
            except sqlite3.OperationalError:
                con.close()
                return None
        results = tuple(zip(*[(
                f'{cls.singleton.skill_list[result[0]].icon} {result[1]}',
                f'{cls.singleton.skill_list[result[0]].icon} '
                f'__{result[1]}__\n{result[2]}',
            )
            for result in cur
        ]))
        con.close()
        return results

    @classmethod
    async def insert_hero_alias(cls, hero, name):
        if name in cls.singleton.unit_names:
            return False
        con = sqlite3.connect("feh/names.db")
        cur = con.cursor()
        if hero.index > 0:
            cur.execute('INSERT INTO heroes (name, id) VALUES (?, ?);',
                        (name, hero.index))
            cls.singleton.unit_names[name] = (
                cls.singleton.unit_list[hero.index])
        else:
            cur.execute('INSERT INTO enemy (name, id) VALUES (?, ?);',
                        (name, hero.index))
            cls.singleton.enemy_names[name] = (
                cls.singleton.enemy_list[abs(hero.index)])
        con.commit()
        con.close()
        return True

    @classmethod
    async def insert_skill_alias(cls, skill, name):
        if name in cls.singleton.skill_names:
            return False
        con = sqlite3.connect("feh/names.db")
        cur = con.cursor()
        cur.execute('INSERT INTO skills (name, id) VALUES (?, ?);',
                    (name, skill.index))
        con.commit()
        con.close()
        cls.singleton.skill_names[name] = cls.singleton.skill_list[skill.index]
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
            'passive_c_id, passive_s_id, refine_id, p_hero_id, p_custom, '
            'p_atk, p_spd, p_def, p_res) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '
            '?, ?, ?, ?, ?, ?);',
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
                hero.p_hero_id, hero.p_custom, hero.p_atk, hero.p_spd,
                hero.p_def, hero.p_res,
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
            'refine_id, p_hero_id, p_custom, p_atk, p_spd, p_def, p_res '
            'FROM user_heroes WHERE user_id = ? AND search_name = ?',
            (user_id, search_name)
        )
        hero_data = cur.fetchone()
        con.close()
        if not hero_data:
            return None
        if hero_data[0] >= 0:
            hero = copy(cls.singleton.unit_list[hero_data[0]])
            hero.equipped = copy(hero.equipped)
        else:
            hero = copy(cls.singleton.enemy_list[abs(hero_data[0])])
            hero.equipped = copy(hero.equipped)
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
        if hero_data[16]:
            if hero_data[17]:
                hero.update_stat_mods(
                    pair=cls.get_custom_hero(hero_data[17], user_id))
            else:
                hero.force_pair(*hero_data[16:22])
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
            'refine_id = ?, p_hero_id = ?, p_custom = ?, p_atk = ?, '
            'p_spd = ?, p_def = ?, p_res = ? WHERE user_id = ? '
            'AND search_name = ?;',
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
                hero.p_hero_id, hero.p_custom, hero.p_atk, hero.p_spd,
                hero.p_def, hero.p_res,
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
