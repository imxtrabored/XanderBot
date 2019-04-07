from discord import Embed

from command.cmd_default import CmdDefault
from command.common import (ReplyPayload,
    format_hero_title, process_hero, process_hero_spaces,
)
from feh.emojilib import EmojiLib as em
from feh.hero import Stat, Rarity
from feh.unitlib import UnitLib


class HeroMerges(CmdDefault):

    help_text = (
        'The ``merges`` command shows a quick summary of the attribute '
        'bonuses from merging extra copies of a hero.\n\n'
        'Usage: ``f?merges {hero name}, {modifier 1}, {modiier 2}, '
        '{additional modifiers...}``'
    )

    @staticmethod
    async def cmd(params, user_id):
        if not params:
            return ReplyPayload(content='No input. Please enter a hero.')
        tokens = params.split(',')
        zoom_state = False
        hero = UnitLib.get_hero(tokens[0], user_id)
        embed = Embed()
        if not hero:
            if ',' not in params:
                hero, bad_args = process_hero_spaces(params, user_id)
            if not hero:
                return ReplyPayload(
                    content=(f'Hero not found: {tokens[0]}. Don\'t forget '
                             'that modifiers should be delimited by commas.'),
                )
            embed.set_footer(
                text=('Please delimit modifiers with commas (,) '
                      'in the future to improve command processing.')
            )
        else:
            hero, bad_args = process_hero(hero, tokens[1:])
        title = format_hero_title(hero)
        bonuses = '\n'.join([
            f'{f"+{merges}".rjust(3)}:'
            f'{"|".join([str(stat).rjust(3) for stat in row])}'
            for merges, row in enumerate(hero.get_merge_table(), 1)
        ])
        description = (
            f'{em.get(Rarity(hero.rarity))} · '
            f'{em.get(Stat.HP )} · '
            f'{em.get(Stat.ATK)} · '
            f'{em.get(Stat.SPD)} · '
            f'{em.get(Stat.DEF)} · '
            f'{em.get(Stat.RES)} · '
            f'BST: {hero.max_total}'
            f'```L{str(hero.level).rjust(2)}:'
            f'{str(hero.max_hp ).rjust(3)}|'
            f'{str(hero.max_atk).rjust(3)}|'
            f'{str(hero.max_spd).rjust(3)}|'
            f'{str(hero.max_def).rjust(3)}|'
            f'{str(hero.max_res).rjust(3)}\n'
            f'{bonuses}```\n'
            f'Dragonflower bonus order:\n'
            f'{hero.merge_order[0][2].name}, '
            f'{hero.merge_order[1][2].name}, '
            f'{hero.merge_order[2][2].name}, '
            f'{hero.merge_order[3][2].name}, '
            f'{hero.merge_order[4][2].name}'
        )
        embed.add_field(name=title, value=description, inline=True)
        if bad_args:
            content = ('I did not understand the following arguments: '
                       f'{", ".join(bad_args)}')
        else: content = ''
        embed.set_thumbnail(
            url=('https://raw.githubusercontent.com/imxtrabored/XanderBot/'
                 f'master/xanderbot/feh/data/heroes/{hero.index}/Face.png')
        )
        embed.color = em.get_color(hero.color)
        return ReplyPayload(content=content, embed=embed)
