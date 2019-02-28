import re

from operator import methodcaller
from string import punctuation, whitespace

from feh.emojilib import EmojiLib as em
from feh.hero import Stat
from feh.skill import SkillType
from feh.unitlib import UnitLib

TRANSTAB = str.maketrans('', '', punctuation + whitespace)
NON_DECIMAL = re.compile(r'[^\d]+')

class DiscordData:
    __slots__ = ('client', 'devs')

    @classmethod
    def setup_commands(cls, client):
        cls.client = client
        cls.devs = []
        cls.devs.append(client.get_user(151913154803269633))
        cls.devs.append(client.get_user(196379129472352256))
        cls.devs.append(client.get_user(248284024097734658))


def filter_name(name):
    return name.lower().replace('+', 'plus').replace('-', 'minus').translate(TRANSTAB)



def format_hero_title(hero):
    if hero.is_legend:
        legend_info = (
            f'{em.get(hero.legend_element)}'
            f'{em.get(hero.legend_boost)}'
        )
    else: legend_info = ''
    title = (
        f'{hero.name}: {hero.epithet} '
        f'{em.get(hero.weapon_type)}'
        f'{em.get(hero.move_type)}'
        f'{legend_info}'
    )
    return title



def process_hero(hero, args):
    bad_args = []
    rarity = None
    merges = None
    boon = None
    bane = None
    level = None
    flowers = None
    for token in args:
        param = filter_name(token[:24])
        # rarity, merges, iv, level, "summoned"
        # regex might be faster or slower here idk
        rarity_test = (param.replace('*', '').replace('stars', '')
                       .replace('star', '').replace('rarity', ''))
        if rarity_test.isdecimal():
            rarity = int(rarity_test)
        elif 'merge' in param:
            merges = int(NON_DECIMAL.sub('', param))
        elif ('plusplus' in param or 'flower' in param
              or param.startswith('df') or param.endswith('df')):
            flowers = int(NON_DECIMAL.sub('', param))
        elif 'plus' in param:
            # this might be merges, iv, or a skill
            plus_test = param.replace('plus', '')
            if plus_test.isdecimal():
                merges = int(plus_test)
            elif (
                    param in [
                        'plushp'       ,
                        'hpplus'       ,
                        'plushitpoint' ,
                        'plushitpoints',
                        'hitpointplus' ,
                        'hitpointsplus',
                    ]
            ):
                boon = Stat.HP
            elif (
                    param in (
                        'plusatk'   ,
                        'atkplus'   ,
                        'plusattack',
                        'attackplus',
                    )
            ):
                boon = Stat.ATK
            elif (
                    param in (
                        'plusspd'  ,
                        'spdplus'  ,
                        'plusspeed',
                        'speedplus',
                    )
            ):
                boon = Stat.SPD
            elif (
                    param in (
                        'plusdef'    ,
                        'defplus'    ,
                        'plusdefense',
                        'defenseplus',
                        'plusdefence',
                        'defenceplus',
                    )
            ):
                boon = Stat.DEF
            elif (
                    param in (
                        'plusres'       ,
                        'resplus'       ,
                        'plusresistance',
                        'resistanceplus',
                    )
            ):
                boon = Stat.RES
            else:
                skill = UnitLib.get_skill(param)
                if skill:
                    if skill.type == SkillType.WEAPON:
                        hero.equipped_weapon = skill
                    elif skill.type == SkillType.ASSIST:
                        hero.equipped_assist = skill
                    elif skill.type == SkillType.SPECIAL:
                        hero.equipped_special = skill
                    elif skill.type == SkillType.PASSIVE_A:
                        if (hero.equipped_passive_a
                                and not hero.equipped_passive_s
                                and skill.is_seal):
                            hero.equipped_passive_s = skill
                        else: hero.equipped_passive_a = skill
                    elif skill.type == SkillType.PASSIVE_B:
                        if (hero.equipped_passive_b
                                and not hero.equipped_passive_s
                                and skill.is_seal):
                            hero.equipped_passive_s = skill
                        else: hero.equipped_passive_b = skill
                    elif skill.type == SkillType.PASSIVE_C:
                        if (hero.equipped_passive_c
                                and not hero.equipped_passive_s
                                and skill.is_seal):
                            hero.equipped_passive_s = skill
                        else: hero.equipped_passive_c = skill
                    elif skill.type == SkillType.PASSIVE_SEAL:
                        hero.equipped_passive_s = skill
                else:
                    bad_args.append(token)
        elif 'boon' in param or 'asset' in param:
            if 'hp' in param or 'hitpoint' in param:
                boon = Stat.HP
            elif 'atk' in param or 'attack' in param:
                boon = Stat.ATK
            elif 'spd' in param or 'speed' in param:
                boon = Stat.SPD
            elif 'def' in param:
                boon = Stat.DEF
            elif 'res' in param:
                boon = Stat.RES
        elif 'minus' in param or 'bane' in param or 'flaw' in param:
            if 'hp' in param or 'hitpoint' in param:
                bane = Stat.HP
            elif 'atk' in param or 'attack' in param:
                bane = Stat.ATK
            elif 'spd' in param or 'speed' in param:
                bane = Stat.SPD
            elif 'def' in param:
                bane = Stat.DEF
            elif 'res' in param:
                bane = Stat.RES
        else:
            skill = UnitLib.get_skill(param)
            if skill:
                if skill.type == SkillType.WEAPON:
                    hero.equipped_weapon = skill
                elif skill.type == SkillType.ASSIST:
                    hero.equipped_assist = skill
                elif skill.type == SkillType.SPECIAL:
                    hero.equipped_special = skill
                elif skill.type == SkillType.PASSIVE_A:
                    if (hero.equipped_passive_a
                            and not hero.equipped_passive_s
                            and skill.is_seal):
                        hero.equipped_passive_s = skill
                    else: hero.equipped_passive_a = skill
                elif skill.type == SkillType.PASSIVE_B:
                    if (hero.equipped_passive_b
                            and not hero.equipped_passive_s
                            and skill.is_seal):
                        hero.equipped_passive_s = skill
                    else: hero.equipped_passive_b = skill
                elif skill.type == SkillType.PASSIVE_C:
                    if (hero.equipped_passive_c
                            and not hero.equipped_passive_s
                            and skill.is_seal):
                        hero.equipped_passive_s = skill
                    else: hero.equipped_passive_c = skill
                elif skill.type == SkillType.PASSIVE_SEAL:
                    hero.equipped_passive_s = skill
            else:
                bad_args.append(token)

    if   boon is None and bane is not None:
        bane = None
        bad_args.append(f'\n{hero.short_name} has flaw but no asset; ignoring flaw')
    elif boon is not None and bane is None:
        if boon != Stat.HP:
            bane = Stat.HP
            bad_args.append(f'\n{hero.short_name} has no flaw; defaulting to HP flaw')
        else:
            bane = Stat.ATK
            bad_args.append(f'\n{hero.short_name} has no flaw; defaulting to Atk flaw')

    hero.update_stat_mods(boon = boon, bane = bane, merges = merges,
                          rarity = rarity, flowers = flowers)

    return hero, bad_args



def process_hero_spaces(params):
    tokens = [filter_name(token) for token in params.split()]
    is_hero = 0
    for i in range(1, len(tokens)):
        if UnitLib.check_name(''.join(tokens[:i])):
            is_hero = i
    if is_hero:
        hero = UnitLib.get_hero(''.join(tokens[:is_hero]))
        return process_hero(hero, tokens[is_hero:])
    else:
        return None, None
