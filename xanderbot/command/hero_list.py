from dataclasses import dataclass

from discord import Embed

from command.cmd_default import CmdDefault
from command.common import ReactMenu, ReplyPayload, ReactEditPayload
from feh.emojilib import EmojiLib as em
from feh.unitlib import UnitLib


PAGE_LIMIT = 24


class HeroList(CmdDefault):

    REACT_MENU = (
        '⬆',
        '⬇',
    )

    @dataclass
    class Data(object):

        __slots__ = (
            'embed', 'results', 'search_param', 'page_start'
        )

        embed: Embed
        results: list
        search_param: str
        page_start: int

    @staticmethod
    def format_list(embed, results, search_param, start=0):
        if not results:
            start = -1
            end = 0
            result = 'No results!'
        else:
            end = min(start + PAGE_LIMIT, len(results))
            result = '\n'.join(results[start:end])
        if search_param:
            matching = f'Heroes matching "{search_param}"'
        else:
            matching = 'All Heroes'
        embed.title = f'{matching} ({start + 1} - {end} of {len(results)}):'
        embed.description = result
        return embed

    @staticmethod
    async def cmd(params, user_id):
        result_list, _, bad_args = UnitLib.sort_heroes(
            (), params, '')
        if result_list is None:
            return ReplyPayload(
                content=('Syntax error. Use ``f?help list`` for help '
                         'with the syntax for this command.'),
                reactable=ReactMenu(
                    emojis=HeroList.REACT_MENU, callback=HeroList.react),
            )
        embed = Embed()
        HeroList.format_list(
            embed, result_list, params, 0)
        if any(bad_args):
            content = ('I did not understand the following: '
                       f'{", ".join(bad_args)}')
        else:
            content = ''
        embed.color = em.get_color(None)
        react_menu = ReactMenu(
            emojis=HeroList.REACT_MENU,
            data=HeroList.Data(embed, result_list, params, 0),
            callback=HeroList.react,
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
        HeroList.format_list(data.embed, data.results, data.search_param,
                             data.page_start)
        return ReactEditPayload(embed=data.embed, delete=True)
