from dataclasses import dataclass

from discord import Embed

from command.cmd_default import CmdDefault
from command.common import (
    DiscordData, ReactMenu, ReplyPayload, ReactEditPayload
)
from feh.emojilib import EmojiLib as em
from feh.unitlib import UnitLib

PAGE_LIMIT = 24


class BarracksList(CmdDefault):

    help_text = (
        'The ``barracks`` command lists all heroes in your barracks.\n\n'
        'Usage: ``f?barracks``\n\n'
        '**About the Barracks**\n'
        'The barracks is a permanent place to save a list of custom unit '
        'builds. Custom names are individual to each summoner, so different '
        'summoners can have different custom heroes with the same custom '
        'name.\n\n'
        'Heroes in the barracks can be used as a hero name for the purposes '
        'of any other command, such as ``f?hero``, ``f?compare``, etc. Their '
        'properties and equipped skills can be futher modified by additional '
        'parameters in a command, just like a normal hero.\n\n'
        'The barracks can be used to keep track of your units, to showcase '
        'your units to other summoners, to keep track of summons, or any '
        'other use imaginable. The current barracks limit is 300 heroes, but '
        'this may be raised in the future.\n\n'
        'For information on saving heroes to your barracks, use ``f?help '
        'save``.'
    )

    REACT_MENU = (
        '⬆',
        '⬇',
    )

    @dataclass
    class Data(object):

        __slots__ = (
            'embed', 'results', 'user_name', 'page_start'
        )

        embed: Embed
        results: list
        user_name: str
        page_start: int

    @staticmethod
    def format_barracks(embed, results, user_name, start=0):
        if not results:
            start = -1
            end = 0
            result = 'Your barracks are empty.'
        else:
            end = min(start + PAGE_LIMIT, len(results))
            result = '\n'.join(results[start:end])
        embed.title = (f'{user_name}\'s Barracks '
                       f'({start + 1} - {end} of {len(results)}):')
        embed.description = result
        embed.set_footer(
            text=f'{len(results)} heroes out of 300 slots',
            icon_url=('https://gamepedia.cursecdn.com/feheroes_gamepedia_en/5/'
                      '59/Structure_Fortress.png')
        )
        return embed

    @staticmethod
    async def cmd(params, user_id):
        hero_list = UnitLib.list_custom_heroes(user_id)
        user_name = DiscordData.client.get_user(user_id).name
        embed = Embed()
        BarracksList.format_barracks(embed, hero_list, user_name, 0)
        embed.color = em.get_color(None)
        react_menu = ReactMenu(
            emojis=BarracksList.REACT_MENU,
            data=BarracksList.Data(embed, hero_list, user_name, 0),
            callback=BarracksList.react,
        )
        return ReplyPayload(embed=embed, reactable=react_menu)

    @staticmethod
    async def react(reaction, data, user_id):
        if not data:
            return ReactEditPayload(delete=True)
        if reaction.emoji == '⬆':
            if data.page_start > 0:
                data.page_start = max(data.page_start - PAGE_LIMIT, 0)
            else:
                return ReactEditPayload(delete=True)
        elif reaction.emoji == '⬇':
            new_start = data.page_start + PAGE_LIMIT
            if new_start < len(data.results):
                data.page_start = new_start
            else:
                return ReactEditPayload(delete=True)
        else:
            return ReactEditPayload()
        BarracksList.format_barracks(
            data.embed, data.results, data.user_name, data.page_start)
        return ReactEditPayload(embed=data.embed, delete=True)
