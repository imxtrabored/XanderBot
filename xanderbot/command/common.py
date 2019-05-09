import re
from string import punctuation, whitespace
from types import FunctionType
from typing import NamedTuple

from discord import Embed

from feh.emojilib import EmojiLib as em
from feh.hero import Stat, LegendElement, LegendStat, SummonerSupport
from feh.unitlib import UnitLib, PARENTHETICAL


TEMP_SEP = '#@@@'
TRANSTAB = str.maketrans('', '', punctuation + whitespace)
BOON_ASSET = re.compile(r'boon|asset')
MINUS_BANE_FLAW = re.compile(r'minus|bane|flaw')
NON_DECIMAL = re.compile(r'[^\d]+')
PLUS_MINUS = re.compile(r'plus|minus')
PLUSPLUS_FLOWER_DF = re.compile(r'plusplus|flower|^df|df$')
WITH_SYNONYMS = re.compile(
    r'\s+(?:with|having|has|using|equip|equipping|equipped)\s+')

LEGEND_TYPES = {
    LegendElement.FIRE : 'Legendary Effect: Fire',
    LegendElement.WATER: 'Legendary Effect: Water',
    LegendElement.WIND : 'Legendary Effect: Wind',
    LegendElement.EARTH: 'Legendary Effect: Earth',
}
MYTHIC_TYPES = {
    LegendElement.LIGHT: 'Mythic Effect: Light',
    LegendElement.DARK : 'Mythic Effect: Dark',
    LegendElement.ASTRA: 'Mythic Effect: Astra',
    LegendElement.ANIMA: 'Mythic Effect: Anima',
}
LEGEND_BOOSTS = {
    LegendStat.ATK: 'Ally Boost: HP+3, Atk+2',
    LegendStat.SPD: 'Ally Boost: HP+3, Spd+3',
    LegendStat.DEF: 'Ally Boost: HP+3, Def+4',
    LegendStat.RES: 'Ally Boost: HP+3, Res+4',
    LegendStat.DUEL: (
        'Ally Boost: +3 HP\n\n'
        'Standard Effect 1: Duel\n'
        'If unit is 5★ and level 40 and unit\'s stats total less than 175, '
        'treats unit\'s stats as 175 in modes like Arena. (Higher-scoring '
        'opponents will appear. Stat total calculation excludes any values '
        'added by merges and skills.)\n'
        'Standard Effect 2: Pair Up\n'
        'An ability that can only be used under certain circumstances. Pair '
        'Up can be accessed from the Interact with Allies menu, and allows '
        'this unit to join battle in a group with another ally.'
    ),
}
MYTHIC_BOOSTS = {
    LegendStat.ATK: 'Boost: HP+5, Atk+3',
    LegendStat.SPD: 'Boost: HP+5, Spd+4',
    LegendStat.DEF: 'Boost: HP+5, Def+5',
    LegendStat.RES: 'Boost: HP+5, Res+5',
    LegendStat.DUEL: 'Invalid boost',
}

SUPPORT_RANKS = {
    'c': 1,
    'b': 2,
    'a': 3,
    's': 4,
}

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
    else:
        legend_info = ''
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
    if hero.is_legend:
        if hero.legend_element in LEGEND_TYPES:
            return (f'{LEGEND_TYPES[hero.legend_element]}\n'
                    f'{LEGEND_BOOSTS[hero.legend_boost]}')
        return (f'{MYTHIC_TYPES[hero.legend_element]}\n'
                f'{MYTHIC_BOOSTS[hero.legend_boost]}')
    return ''


def try_equip(hero, skill_name):
    skill = UnitLib.get_skill(skill_name)
    if not skill:
        return 0
    if not hero.equip(skill):
        return 1
    return 2


def process_hero_args(hero, args, *, defer_iv_match=False):
    bad_args = []
    not_allowed = []
    rarity = None
    merges = None
    boon = None
    bane = None
    level = None
    flowers = None
    support = None
    for token in args:
        filtered = filter_name(token[:40])
        # rarity, merges, iv, level, "summoned"
        rarity_test = (filtered.replace('*', '').replace('stars', '')
                       .replace('star', '').replace('rarity', ''))
        if rarity_test.isdecimal():
            rarity = int(rarity_test)
        elif 'merge' in filtered:
            merge_test = filtered.replace('merges', '').replace('merge', '')
            if merge_test.isdecimal():
                merges = int(merge_test)
            else:
                bad_args.append(token.strip())
        elif PLUSPLUS_FLOWER_DF.search(filtered) is not None:
            plus_test = NON_DECIMAL.sub('', filtered)
            if plus_test.isdecimal():
                flowers = int(plus_test)
            else:
                equip_status = try_equip(hero, filtered)
                if equip_status == 0:
                    bad_args.append(token.strip())
                elif equip_status == 1:
                    not_allowed.append(token.strip())
        elif 'plus' in filtered:
            # this might be merges, iv, or a skill
            plus_test = filtered.replace('plus', '')
            if plus_test.isdecimal():
                merges = int(plus_test)
            else:
                stat = Stat.get_by_name(plus_test)
                if stat is not None:
                    boon = stat
                else:
                    if 'minus' in filtered:
                        iv_order = PLUS_MINUS.findall(filtered)
                        iv_tokens = tuple(filter(
                            None, PLUS_MINUS.split(filtered)))
                        if len(iv_order) == 2:
                            if len(iv_tokens) == 2:
                                if iv_order[0] == 'plus':
                                    boon = Stat.get_by_name(iv_tokens[0])
                                    bane = Stat.get_by_name(iv_tokens[1])
                                else:
                                    boon = Stat.get_by_name(iv_tokens[1])
                                    bane = Stat.get_by_name(iv_tokens[0])
                            elif len(iv_tokens) == 1:
                                stat2 = None
                                for i in range(3, len(iv_tokens[0])):
                                    stat1 = Stat.get_by_name(iv_tokens[0][:i])
                                    if stat1 is not None:
                                        stat2 = Stat.get_by_name(
                                            iv_tokens[0][i:])
                                        if stat2 is not None:
                                            break
                                if stat1 is not None and stat2 is not None:
                                    if iv_order[0] == 'plus':
                                        boon = stat1
                                        bane = stat2
                                    else:
                                        boon = stat2
                                        bane = stat1
                                else:
                                    bad_args.append(token.strip())
                            else:
                                bad_args.append(token.strip())
                        else:
                            bad_args.append(token.strip())
                    else:
                        # "minus" does not appear in any skill names
                        equip_status = try_equip(hero, filtered)
                        if equip_status == 0:
                            bad_args.append(token.strip())
                        elif equip_status == 1:
                            not_allowed.append(token.strip())
        elif 'boon' in filtered or 'asset' in filtered:
            asset_test = filtered.replace('boon', '').replace('asset', '')
            stat = Stat.get_by_name(asset_test)
            if stat is not None:
                boon = stat
        elif 'minus' in filtered or 'bane' in filtered or 'flaw' in filtered:
            flaw_test = (filtered.replace('minus', '').replace('bane', '')
                         .replace('flaw', ''))
            stat = Stat.get_by_name(flaw_test)
            if stat is not None:
                bane = stat
        elif 'support' in filtered:
            supp_test = filtered.replace('support', '')
            if supp_test.isdecimal():
                support = int(supp_test)
            elif supp_test in SUPPORT_RANKS:
                support = SUPPORT_RANKS[supp_test]
            else:
                bad_args.append(token.strip())
        elif 'summoned' in filtered:
            max_rarity = rarity or hero.rarity
            hero.equip(next((s[0] for s in hero.weapon[::-1]
                             if s[2] and s[2] <= max_rarity), None))
            hero.equip(next((s[0] for s in hero.assist[::-1]
                             if s[2] and s[2] <= max_rarity), None))
            hero.equip(next((s[0] for s in hero.special[::-1]
                             if s[2] and s[2] <= max_rarity), None))
        elif 'prf' in filtered:
            if hero.weapon_prf is not None:
                hero.equip(hero.weapon_prf)
            else:
                not_allowed.append(token.strip())
        else:
            equip_status = try_equip(hero, filtered)
            if equip_status == 0:
                bad_args.append(token.strip())
            elif equip_status == 1:
                not_allowed.append(token.strip())
    if not defer_iv_match:
        if boon is None and bane is not None:
            bane = None
        elif boon is not None and bane is None:
            if boon != Stat.HP:
                bane = Stat.HP
            else:
                bane = Stat.RES
    hero.update_stat_mods(boon=boon, bane=bane, merges=merges, rarity=rarity,
                          flowers=flowers, summ_support=support)
    return hero, bad_args, not_allowed


def process_hero_spaces(params, user_id):
    tokens = [filter_name(token) for token in params.split()]
    match_hero = None
    match_hero_index = 0
    for i in range(1, len(tokens)):
        hero = UnitLib.get_hero(''.join(tokens[:i]), user_id)
        if hero:
            match_hero = hero
            match_hero_index = i
    if match_hero:
        return process_hero_args(match_hero, tokens[match_hero_index:])
    return None, params, ()


def process_hero(params, user_id):
    if not params:
        return None, '', False
    tokens = PARENTHETICAL.sub(
        lambda match: match.group().replace(',', TEMP_SEP), params)
    tokens = WITH_SYNONYMS.split(tokens, maxsplit=1)
    if len(tokens) < 2 and ',' in params:
        tokens = params.split(',', 1)
    if len(tokens) > 1:
        hero_args = tokens[1].split(',')
    else:
        hero_args = ()
    hero = UnitLib.get_hero(tokens[0], user_id)
    if not hero:
        if ',' not in params:
            no_commas = True
            hero, bad_args, not_allowed = process_hero_spaces(params, user_id)
        else:
            hero, bad_args, not_allowed, no_commas = (
                None, tokens[0], None, False)
    else:
        no_commas = False
        hero, bad_args, not_allowed = process_hero_args(hero, hero_args)
        if bad_args and len(hero_args) == 1:
            hero, bad_args, not_allowed = (
                process_hero_args(hero, hero_args[0].split()))
            no_commas = True
    return hero, bad_args, not_allowed, no_commas
