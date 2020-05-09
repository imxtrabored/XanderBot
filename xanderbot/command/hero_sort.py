import re
from dataclasses import dataclass

from discord import Embed

from command.cmd_default import CmdDefault
from command.common import (
    ReactMenu, ReplyPayload, ReactEditPayload, WITH_SYNONYMS)
from feh.emojilib import EmojiLib as em
from feh.unitlib import UnitLib

FROM_SYNONYMS = re.compile(r'(?:\s+|^)(?:in|from|within|among(?:st)?)\s+')

PAGE_LIMIT = 24


class HeroSort(CmdDefault):

    help_text = (
        'The ``sort`` command displays all heroes in the game that match '
        'the search terms ordered by the specified sort terms.\n\n'
        'Usage: ``f?sort {sort terms} from {search terms} with {modifiers}``'
        '\n\n'
        'The sort terms can contain any number of any hero attribute (hp, '
        'atk, spd, def, res), any of the four basic arithmetic operators '
        '(+ - * /), and the attributes color, weapon, or move, separated by '
        'commas. Each attribute can be optionally reduced to one letter. This '
        'allows for flexibly searching for the top heroes in any category.\n\n'
        'Example Searches:\n'
        '``f?sort h + d`` will sort all heroes by their total physical bulk '
        '(HP + Def).\n'
        '``f?sort d * r, h from dragons`` will sort all dragons by Def * Res, '
        'then by HP. This shows which dragon units make the best mixed tanks '
        '(since Def * Res biases towards units with equally high values in '
        'both).\n'
        '``f?sort cwma from prf with prf, +atk`` will show each hero that has '
        'a Prf weapon skill ordered by the categories Color, Weapon type, and '
        'Move type. Within each category, the heroes are sorted by their '
        'total Atk stat when their Prf weapon is equipped and with an asset '
        'in Attack.\n\n'
        'Note that the hero modifiers work slightly differently for this '
        'command. When multiple skills for the same slot are provided, each '
        'hero will equip the _first_ skill that they are able to equip. For '
        'example, ``f?sort a from blue mages with prf, thoron+`` will equip '
        'each hero with access to a Prf weapon with that Prf weapon, and each '
        'other hero will be equipped with Thoron+.\n\n'
        'The search terms for this command use the same "Special syntax for '
        'search" rules as the ``list`` command; see ``f?help list`` for '
        'details.'
    )

    REACT_MENU = (
        '⬆',
        '⬇',
    )

    @dataclass
    class Data(object):

        __slots__ = (
            'embed', 'results', 'search_param', 'sort_param', 'page_start',
            'page_limit'
        )

        embed: Embed
        results: list
        search_param: str
        sort_param: str
        page_start: int
        page_limit: int

    @staticmethod
    def format_sort(embed, results, search_param, sort_param, start=0,
                    page_limit=PAGE_LIMIT):
        if not results:
            start = -1
            end = 0
            result = 'No results!'
        else:
            while True:
                end = min(start + page_limit, len(results))
                result = '\n'.join(results[start:end])
                if len(result) < 2000:
                    break
                page_limit -= 4
        if search_param:
            matching = f' matching "{search_param}"'
        else:
            matching = ''
        embed.title = (
            f'Heroes{matching} sorted by ({sort_param or "None"}) '
            f'({start + 1} - {end} of {len(results)}):')
        embed.description = result
        return embed, page_limit

    @staticmethod
    async def cmd(params, user_id):
        tokens = FROM_SYNONYMS.split(params.lower(), maxsplit=1)
        if len(tokens) > 1:
            sort_terms = tokens[0].split(',')
            tokens = WITH_SYNONYMS.split(tokens[1], maxsplit=1)
            search_terms = tokens[0]
        else:
            search_terms = None
            tokens = WITH_SYNONYMS.split(tokens[0], maxsplit=1)
            sort_terms = tokens[0].split(',')
        if len(tokens) > 1:
            equip_terms = tokens[1]
        else:
            equip_terms = None
        sorted_heroes, sort_terms, bad_args = UnitLib.sort_heroes(
            sort_terms, search_terms, equip_terms, user_id)
        if sorted_list is None:
            return ReplyPayload(
                content=('Syntax error. Use ``f?help sort`` for help '
                         'with the syntax for this command.'),
                reactable=ReactMenu(
                    emojis=HeroSort.REACT_MENU, callback=HeroSort.react),
            )
        embed = Embed()
        embed, page_limit = HeroSort.format_sort(
            embed, sorted_list, search_terms, sort_terms, 0, PAGE_LIMIT)
        if any(bad_args):
            content = ('I did not understand the following: '
                       f'{", ".join(bad_args)}')
        else:
            content = ''
        embed.color = em.get_color(None)
        react_menu = ReactMenu(
            emojis=HeroSort.REACT_MENU,
            data=HeroSort.Data(
                embed, sorted_list, search_terms, sort_terms, 0, page_limit),
            callback=HeroSort.react,
        )
        return ReplyPayload(content=content, embed=embed, reactable=react_menu)

    @staticmethod
    async def react(reaction, data, user_id):
        if not data:
            return ReactEditPayload(delete=True)
        elif reaction.emoji == '⬆':
            if data.page_start > 0:
                page_size = PAGE_LIMIT
                data.page_start = max(data.page_start - page_size, 0)
            else:
                return ReactEditPayload(delete=True)
        elif reaction.emoji == '⬇':
            page_size = PAGE_LIMIT
            new_start = data.page_start + page_size
            if new_start < len(data.results):
                data.page_start = new_start
            else:
                return ReactEditPayload(delete=True)
        else:
            return ReactEditPayload()
        data.embed, data.page_limit = HeroSort.format_sort(
            data.embed, data.results, data.search_param, data.sort_param,
            data.page_start, data.page_limit)
        return ReactEditPayload(embed=data.embed, delete=True)
