import re
from string import punctuation, whitespace
from types import FunctionType
from typing import NamedTuple

from discord import Embed

from feh.emojilib import EmojiLib as em
from feh.hero import Stat, LegendElement, LegendStat, SummonerSupport
from feh.unitlib import UnitLib


TRANSTAB = str.maketrans('', '', punctuation + whitespace)
NON_DECIMAL = re.compile(r'[^\d]+')


class DiscordData:

    __slots__ = ('client', 'devs')

    @classmethod
    async def setup_commands(cls, client):
        cls.client = client
        cls.devs = []
        cls.devs.append(await client.get_user_info(151913154803269633))
        cls.devs.append(await client.get_user_info(196379129472352256))
        cls.devs.append(await client.get_user_info(248284024097734658))


class ReactMenu(NamedTuple):
    emojis: tuple = ()
    data: object = None
    callback: FunctionType = None
    self_destruct: bool = False

class UserPrompt(NamedTuple):
    callback: FunctionType = None
    fallback: FunctionType = None
    content: str = None
    embed: Embed = None
    data: object = None

class ReplyPayload(NamedTuple):
    content: str = None
    embed: Embed = None
    reactable: ReactMenu = None
    replyable: UserPrompt = None

class ReactEditPayload(NamedTuple):
    content: str = None
    embed: Embed = None
    delete: bool = False
    replyable: UserPrompt = None
    self_destruct: bool = False


def filter_name(name):
    return (name.lower().replace('+', 'plus').replace('-', 'minus')
            .translate(TRANSTAB))


def format_hero_title(hero):
    if hero.is_legend:
        legend_info = (
            f'{em.get(hero.legend_element)}'
            f'{em.get(hero.legend_boost)}'
        )
    else: legend_info = ''
    if hero.custom_name:
        name = f'{hero.custom_name} [{hero.short_name}]'
    else:
        name = f'{hero.name}: {hero.epithet} '
    if hero.summ_support > 0:
        support = em.get(SummonerSupport(hero.summ_support))
    else:
        support = ''
    title = (
        f'{name} {em.get(hero.weapon_type)}{em.get(hero.move_type)}'
        f'{legend_info}{support}'
    )
    return title


def format_legend_eff(hero):
    legend_types = {
        LegendElement.FIRE : 'Legendary Effect: Fire',
        LegendElement.WATER: 'Legendary Effect: Water',
        LegendElement.WIND : 'Legendary Effect: Wind',
        LegendElement.EARTH: 'Legendary Effect: Earth',
    }
    mythic_types = {
        LegendElement.LIGHT: 'Mythic Effect: Light',
        LegendElement.DARK : 'Mythic Effect: Dark',
        LegendElement.ASTRA: 'Mythic Effect: Astra',
        LegendElement.ANIMA: 'Mythic Effect: Anima',
    }
    legend_boosts = {
        LegendStat.ATK: 'Ally Boost: HP+3, Atk+2',
        LegendStat.SPD: 'Ally Boost: HP+3, Spd+3',
        LegendStat.DEF: 'Ally Boost: HP+3, Def+4',
        LegendStat.RES: 'Ally Boost: HP+3, Res+4',
        LegendStat.DUEL: (
            'Ally Boost: +3 HP\nIf unit is 5★ and level 40 and unit\'s stats '
            'total less than 175, treats unit\'s stats as 175 in modes like '
            'Arena. (Higher-scoring opponents will appear. Stat total '
            'calculation excludes any values added by merges and skills.) '
            'Enables pair-up in certain modes.'
        ),
    }
    mythic_boosts = {
        LegendStat.ATK: 'Boost: HP+5, Atk+3',
        LegendStat.SPD: 'Boost: HP+5, Spd+4',
        LegendStat.DEF: 'Boost: HP+5, Def+5',
        LegendStat.RES: 'Boost: HP+5, Res+5',
        LegendStat.DUEL: 'Invalid boost',
    }
    if hero.is_legend:
        if hero.legend_element in legend_types:
            return (f'{legend_types[hero.legend_element]}\n'
                    f'{legend_boosts[hero.legend_boost]}')
        return (f'{mythic_types[hero.legend_element]}\n'
                f'{mythic_boosts[hero.legend_boost]}')
    return ''


def try_equip(hero, skill_name):
    skill = UnitLib.get_skill(skill_name)
    return skill and hero.equip(skill)


def process_hero(hero, args):
    bad_args = []
    rarity = None
    merges = None
    boon = None
    bane = None
    level = None
    flowers = None
    support = None
    for token in args:
        param = filter_name(token[:40])
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
            plus_test = NON_DECIMAL.sub('', param)
            if plus_test.isdecimal():
                flowers = int(plus_test)
            else:
                if not try_equip(hero, param):
                    bad_args.append(token.strip())
        elif 'plus' in param:
            # this might be merges, iv, or a skill
            plus_test = param.replace('plus', '')
            if plus_test.isdecimal():
                merges = int(plus_test)
            else:
                stat = Stat.get_by_name(plus_test)
                if stat is not None:
                    boon = stat
                else:
                    if not try_equip(hero, param):
                        bad_args.append(token.strip())
        elif 'boon' in param or 'asset' in param:
            asset_test = param.replace('boon', '').replace('asset', '')
            stat = Stat.get_by_name(asset_test)
            if stat is not None:
                boon = stat
        elif 'minus' in param or 'bane' in param or 'flaw' in param:
            flaw_test = (param.replace('minus', '').replace('bane', '')
                         .replace('flaw', ''))
            stat = Stat.get_by_name(flaw_test)
            if stat is not None:
                bane = stat
        elif 'support' in param:
            supp_test = param.replace('support', '')
            if supp_test.isdecimal():
                support = int(supp_test)
            elif supp_test == 'c':
                support = 1
            elif supp_test == 'b':
                support = 2
            elif supp_test == 'a':
                support = 3
            elif supp_test == 's':
                support = 4
            else:
                bad_args.append(token.strip())
        elif 'summoned' in param:
            if rarity:
                max_rarity = rarity
            else:
                max_rarity = hero.rarity
            hero.equip(next((s[0] for s in hero.weapon [::-1]
                             if s[2] and s[2] <= max_rarity), None))
            hero.equip(next((s[0] for s in hero.assist [::-1]
                             if s[2] and s[2] <= max_rarity), None))
            hero.equip(next((s[0] for s in hero.special[::-1]
                             if s[2] and s[2] <= max_rarity), None))
        else:
            if not try_equip(hero, param):
                bad_args.append(token)
    if boon is None and bane is not None:
        bane = None
        bad_args.append(
            f'\n{hero.short_name} has flaw but no asset; ignoring flaw')
    elif boon is not None and bane is None:
        if boon != Stat.HP:
            bane = Stat.HP
            if max(merges, hero.merges) > 0:
                bad_args.append(
                    f'\n{hero.short_name} guessing patched flaw was HP')
            else:
                bad_args.append(
                    f'\n{hero.short_name} no flaw given; guessing HP')
        else:
            bane = Stat.RES
            if max(merges, hero.merges) > 0:
                bad_args.append(
                    f'\n{hero.short_name} guessing patched flaw was Res')
            else:
                bad_args.append(
                    f'\n{hero.short_name} no flaw given; guessing Res')
    hero.update_stat_mods(boon=boon, bane=bane, merges=merges, rarity=rarity,
                          flowers=flowers, summ_support=support)
    return hero, bad_args


def process_hero_spaces(params, user_id):
    tokens = [filter_name(token) for token in params.split()]
    is_hero = 0
    for i in range(1, len(tokens)):
        if UnitLib.check_name(''.join(tokens[:i])):
            is_hero = i
    if is_hero:
        hero = UnitLib.get_hero(''.join(tokens[:is_hero]), user_id)
        return process_hero(hero, tokens[is_hero:])
    return None, None
