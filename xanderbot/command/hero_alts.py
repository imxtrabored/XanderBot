from discord import Embed

from command.cmd_default import CmdDefault, ReplyPayload
from command.common import process_hero
from feh.emojilib import EmojiLib as em


class HeroAlts(CmdDefault):

    help_text = (
        'The ``alts`` command lists the alternate appearances of heroes that '
        'appear more than once, such as seasonal forms or legendary '
        'heroes.\n\n'
        'Usage: ``f?alts {hero name}``'
    )

    @staticmethod
    async def cmd(params, user_id):
        if not params:
            return ReplyPayload(content='No input. Please enter a hero.')
        hero, bad_args, no_commas = process_hero(params, user_id)
        if not hero:
            return ReplyPayload(
                content=(
                    f'Hero not found: {bad_args}. Don\'t forget that '
                    'modifiers should be delimited by commas.'
                )
            )
        embed = Embed()
        if no_commas:
            embed.set_footer(
                text=('Please delimit modifiers with commas (,) '
                      'in the future to improve command processing.')
            )
        embed.title = ('Heroes that are versions of '
                       f'{hero.alt_base.short_name}:')
        embed.description = '\n'.join([
            f'{em.get(alt.weapon_type)}{em.get(alt.move_type)} '
            f'{alt.name}: {alt.epithet} [{alt.short_name}]'
            for alt in hero.alt_base.alt_list
        ])
        embed.color = em.get_color(hero.color)
        embed.set_thumbnail(
            url=('https://raw.githubusercontent.com/imxtrabored/XanderBot/'
                 f'master/xanderbot/feh/data/heroes/{hero.index}/Face.png')
        )
        return ReplyPayload(embed=embed)
