from discord import Embed

from command.cmd_default import CmdDefault
from command.common import ReplyPayload, format_hero_title, process_hero
from feh.emojilib import EmojiLib as em
from feh.hero import Stat, Rarity


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
            f'{hero.merge_order[0][2].short}, '
            f'{hero.merge_order[1][2].short}, '
            f'{hero.merge_order[2][2].short}, '
            f'{hero.merge_order[3][2].short}, '
            f'{hero.merge_order[4][2].short}'
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
