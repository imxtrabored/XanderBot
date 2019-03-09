import discord

from command.cmd_default import CmdDefault
from command.common import filter_name, format_hero_title

from feh.emojilib import EmojiLib as em
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
    'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{}/Full.png'   ,
    'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{}/Battle.png' ,
    'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{}/Special.png',
    'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{}/Hurt.png'   ,
)


class HeroArt(CmdDefault):

    help_text = (
        'The ``art`` command displays the in-game artwork for a hero.\n\n'
        'Usage: ``f?art {hero name}, {art type}``\n\n'
        'Art types include "portrait" (default), "attack", "special", or '
        '"damaged", along with several aliases for each.'
    )

    @staticmethod
    async def cmd(params):
        tokens = params.split(',')
        if not tokens:
            return 'No input detected!', None, None
        hero = UnitLib.get_hero(tokens[0])
        if not hero: return f'Hero not found: {tokens[0]}.', None, [None, 0]
        embed = discord.Embed()
        title = format_hero_title(hero)
        description = f'🖋 {hero.artist}'

        art_index = 0
        if hero.is_enemy != 1:
            for token in tokens:
                param = filter_name(token)
                if param in art_names:
                    art_index = art_names[param]

        embed.add_field(name = title, value = '-', inline = False)
        embed.set_image(url = ART_URLS[art_index].format(hero.id))
        embed.color = em.get_color(hero.color)
        embed.set_footer(text = description)

        #embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{hero.id}/Face.png')

        return None, embed, [hero, art_index]


    @staticmethod
    async def finalize(bot_reply):
        await bot_reply.add_reaction('⬅')
        await bot_reply.add_reaction('➡')


    @staticmethod
    async def react(reaction, bot_msg, embed, data):
        if   reaction.emoji == '⬅':
            if data[0].is_enemy != 1: data[1] = (data[1] - 1) % 4
        elif reaction.emoji == '➡':
            if data[0].is_enemy != 1: data[1] = (data[1] + 1) % 4
        elif reaction.emoji == '👁':
            embed.set_author(name=str(data[0].id))
        else: return None, None, False
        embed.set_image(url = ART_URLS[data[1]].format(data[0].id))
        return None, embed, True
