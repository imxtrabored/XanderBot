from dataclasses import dataclass

from discord import Embed

from command.cmd_default import CmdDefault
from command.common import (
    ReactMenu, ReplyPayload, ReactEditPayload,
    SPLITTER, filter_name, format_hero_title, format_legend_eff, process_hero,
    process_hero_spaces,
)
from feh.emojilib import EmojiLib as em
from feh.hero import Hero
from feh.unitlib import UnitLib


art_names = {
    'full'    : 0,
    'portrait': 0,
    'default' : 0,
    'battle'  : 1,
    'fight'   : 1,
    'attack'  : 1,
    'special' : 2,
    'critical': 2,
    'hurt'    : 3,
    'damaged' : 3,
    'injured' : 3,
}


ART_URLS = (
    'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/'
    'feh/data/heroes/{}/Full.png'   ,
    'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/'
    'feh/data/heroes/{}/Battle.png' ,
    'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/'
    'feh/data/heroes/{}/Special.png',
    'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/'
    'feh/data/heroes/{}/Hurt.png'   ,
)


class HeroArt(CmdDefault):

    help_text = (
        'The ``art`` command displays the in-game artwork for a hero.\n\n'
        'Usage: ``f?art {hero name}, {art type}``\n\n'
        'Art types include "portrait" (default), "attack", "special", or '
        '"damaged", along with several aliases for each.'
    )

    @dataclass
    class Data(object):

        __slots__ = ('embed', 'hero', 'art_index')

        embed: Embed
        hero: Hero
        art_index: int

    REACT_MENU = (
        '⬅',
        '➡',
    )

    @staticmethod
    async def cmd(params, user_id):
        if not params:
            return ReplyPayload(
                content='No input. Please enter a hero.',
                reactable=ReactMenu(
                    emojis=HeroArt.REACT_MENU, callback=HeroArt.react)
            )
        tokens = SPLITTER.split(params)
        hero = UnitLib.get_hero(tokens[0], user_id)
        embed = Embed()
        if not hero:
            if ',' not in params:
                hero, bad_args = process_hero_spaces(params, user_id)
            if not hero:
                return ReplyPayload(
                    content=f'Hero not found: {tokens[0]}.',
                    reactable=ReactMenu(
                        emojis=HeroArt.REACT_MENU,callback=HeroArt.react)
                )
            embed.set_footer(
                text=('Please delimit modifiers with commas (,) '
                      'in the future to improve command processing.')
            )
        else:
            hero, bad_args = process_hero(hero, tokens[1:])
        title = format_hero_title(hero)
        description = f'🖋 {hero.artist}'
        art_index = 0
        if hero.is_enemy != 1:
            for token in tokens:
                param = filter_name(token)
                if param in art_names:
                    art_index = art_names[param]
        embed.add_field(name=title, value='-', inline=False)
        embed.set_image(url=ART_URLS[art_index].format(hero.index))
        embed.color = em.get_color(hero.color)
        embed.set_footer(text=description)
        #embed.set_thumbnail(
        #    url='https://raw.githubusercontent.com/imxtrabored/XanderBot/'
        #    f'master/xanderbot/feh/data/heroes/{hero.index}/Face.png'
        #)
        react_menu = ReactMenu(
            emojis=HeroArt.REACT_MENU,
            data=HeroArt.Data(embed, hero, art_index),
            callback=HeroArt.react,
        )
        return ReplyPayload(None, embed, react_menu, None)


    @staticmethod
    async def react(reaction, data, user_id):
        if not data:
            return ReactEditPayload(delete=True)
        if reaction.emoji == '⬅':
            if data.hero.is_enemy != 1:
                data.art_index = (data.art_index - 1) % 4
            else:
                return ReactEditPayload(delete=True)
        elif reaction.emoji == '➡':
            if data.hero.is_enemy != 1:
                data.art_index = (data.art_index + 1) % 4
            else:
                return ReactEditPayload(delete=True)
        elif reaction.emoji == '👁':
            data.embed.set_author(name=str(data.hero.index))
        else:
            return ReactEditPayload()
        data.embed.set_image(
            url=ART_URLS[data.art_index].format(data.hero.index))
        return ReactEditPayload(embed=data.embed, delete=True)
