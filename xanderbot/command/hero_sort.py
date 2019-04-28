import re
from dataclasses import dataclass

from discord import Embed

from command.cmd_default import CmdDefault
from command.common import ReactMenu, ReplyPayload, ReactEditPayload
from feh.emojilib import EmojiLib as em
from feh.unitlib import UnitLib

FROM_SYNONYMS = re.compile(r'(?:\s+|^)(?:in|from|within|among(?:st)?)\s+')

PAGE_LIMIT = 20


class HeroSort(CmdDefault):

    REACT_MENU = (
        '⬆',
        '⬇',
    )

    @dataclass
    class Data(object):

        __slots__ = (
            'embed', 'results', 'search_param', 'sort_param', 'page_start'
        )

        embed: Embed
        results: list
        search_param: str
        sort_param: str
        page_start: int

    @staticmethod
    def format_sort(embed, results, search_param, sort_param, start=0):
        if not results:
            start = -1
            end = 0
            result = 'No results!'
        else:
            end = min(start + PAGE_LIMIT, len(results))
            result = '\n'.join(results[start:end])
        if search_param:
            matching = f' matching "{search_param}"'
        else:
            matching = ''
        embed.title = (
            f'Heroes{matching} sorted by ({sort_param or "None"}) '
            f'({start + 1} - {end} of {len(results)}):')
        embed.description = result
        return embed

    @staticmethod
    async def cmd(params, user_id):
        if not params:
            return ReplyPayload(
                content='No input.',
                reactable=ReactMenu(
                    emojis=HeroSort.REACT_MENU, callback=HeroSort.react),
            )
        tokens = FROM_SYNONYMS.split(params, maxsplit=1)
        sort_terms = tokens[0].split(',')
        if len(tokens) > 1:
            search_terms = tokens[1]
        else:
            search_terms = None
        sorted_list, sort_terms = UnitLib.sort_heroes(
            sort_terms, search_terms)
        if sorted_list is None:
            return ReplyPayload(
                content=('Syntax error. Use ``f?help sort`` for help '
                         'with the syntax for this command.'),
                reactable=ReactMenu(
                    emojis=HeroSort.REACT_MENU, callback=HeroSort.react),
            )
        embed = Embed()
        HeroSort.format_sort(
            embed, sorted_list, search_terms, sort_terms, 0)
        embed.color = em.get_color(None)
        react_menu = ReactMenu(
            emojis=HeroSort.REACT_MENU,
            data=HeroSort.Data(
                embed, sorted_list, search_terms, sort_terms, 0),
            callback=HeroSort.react,
        )
        return ReplyPayload(embed=embed, reactable=react_menu)

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
        HeroSort.format_sort(data.embed, data.results, data.search_param,
                             data.sort_param, data.page_start)
        return ReactEditPayload(embed=data.embed, delete=True)
