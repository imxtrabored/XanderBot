import discord

from command.cmd_default import CmdDefault
from feh.emojilib import EmojiLib as em
from feh.unitlib import UnitLib

class HeroAlts(CmdDefault):

    help_text = (
        'The ``alts`` command lists the alternate appearances of heroes that '
        'appear more than once, such as seasonal forms or legendary heroes.\n\n'
        'Usage: ``f?alts {hero name}``'
    )

    @staticmethod
    async def cmd(params):
        tokens = params.split(',')
        if not tokens:
            return 'No input detected!', None, None
        zoom_state = False
        hero = UnitLib.get_hero(tokens[0])
        if not hero: return f'Hero not found: {tokens[0]}.', None, None
        embed = discord.Embed()
        embed.title = f'Heroes that are versions of {hero.alt_base.short_name}:'
        embed.description = '\n'.join([
            f'{em.get(alt.weapon_type)}{em.get(alt.move_type)} '
            f'{alt.name}: {alt.epithet} [{alt.short_name}]'
            for alt in hero.alt_base.alt_list
        ])
        embed.color = em.get_color(hero.color)

        embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{hero.id}/Face.png')

        return None, embed, [hero, zoom_state]
