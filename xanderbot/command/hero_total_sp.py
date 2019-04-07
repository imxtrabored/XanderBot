from discord import Embed

from command.cmd_default import CmdDefault
from command.common import (
    ReplyPayload, format_hero_title, process_hero, process_hero_spaces)
from feh.emojilib import EmojiLib as em
from feh.skill import Skill
from feh.unitlib import UnitLib

class HeroTotalSp(CmdDefault):
    """description of class"""

    help_text = (
        'The ``totalsp`` command lists the total amount of SP needed to learn '
        'a hero\'s equipped skills.\n\n'
        'Usage: ``f?totalsp {hero name}, {modifier 1}, {modifier 2}, '
        '{additional modifiers...}``\n\n'
        'Note: This command will be redesigned soon to make it more useful.\n'
        'For help on hero modifier syntax, use ``f?help syntax``.'
    )

    @staticmethod
    async def cmd(params, user_id):
        if not params:
            return ReplyPayload(content='No input. Please enter a hero.')
        tokens = params.split(',')
        hero = UnitLib.get_hero(tokens[0], user_id)
        embed = Embed()
        if not hero:
            if ',' not in params:
                hero, bad_args = process_hero_spaces(params, user_id)
            if not hero:
                return ReplyPayload(
                    content=(
                        f'Hero not found: {tokens[0]}. Don\'t forget that '
                        'modifiers should be delimited by commas.'
                    )
                )
            embed.set_footer(
                text=('Please delimit modifiers with commas (,) '
                      'in the future to improve command processing.')
            )
        else:
            hero, bad_args = process_hero(hero, tokens[1:])
        title = format_hero_title(hero)
        sp_rows = []
        total_sp = 0
        if any(hero.equipped):
            skills = (
                hero.equipped.weapon or Skill.EMPTY_WEAPON,
                hero.equipped.assist or Skill.EMPTY_ASSIST,
                hero.equipped.special or Skill.EMPTY_SPECIAL,
                hero.equipped.passive_a or Skill.EMPTY_PASSIVE_A,
                hero.equipped.passive_b or Skill.EMPTY_PASSIVE_B,
                hero.equipped.passive_c or Skill.EMPTY_PASSIVE_C,
            )
            for skill in skills:
                sp = skill.get_cumul_sp_recursive()
                total_sp += sp
                inherit_sp = (
                    sp * 3 // 2
                    - (skill.refine_sp // 2 if skill.refine_path else 0)
                )
                sp_rows.append(
                    f'{skill.icon}: **{sp} SP** '
                    f'(**{inherit_sp} SP**) · '
                    f'{skill.name}')
            total_sp_text = (
                f'Total SP: **{total_sp}**\n'
                'Total SP if all skills are inherited: '
                f'**{total_sp * 3 // 2}**'
            )
        else:
            skills = (
                next((s[0] for s in hero.weapon[::-1] if s[1] <= hero.rarity),
                     Skill.EMPTY_WEAPON),
                next((s[0] for s in hero.assist[::-1] if s[1] <= hero.rarity),
                     Skill.EMPTY_ASSIST),
                next((s[0] for s in hero.special[::-1] if s[1] <= hero.rarity),
                     Skill.EMPTY_SPECIAL),
                next((s[0] for s in hero.passive_a[::-1]
                      if s[1] <= hero.rarity), Skill.EMPTY_PASSIVE_A),
                next((s[0] for s in hero.passive_b[::-1]
                      if s[1] <= hero.rarity), Skill.EMPTY_PASSIVE_B),
                next((s[0] for s in hero.passive_c[::-1]
                      if s[1] <= hero.rarity), Skill.EMPTY_PASSIVE_C),
            )
            for skill in skills:
                sp = skill.get_cumul_sp_recursive()
                total_sp += sp
                sp_rows.append(f'{skill.icon}: **{sp} SP** · {skill.name}')
            total_sp_text = f'Total SP: **{total_sp}**\n'
        sp_desc = '\n'.join(sp_rows)
        description = f'{sp_desc}\n\n{total_sp_text}'
        embed.add_field(name=title, value=description, inline=True)
        embed.color = em.get_color(hero.color)
        embed.set_thumbnail(
            url=('https://raw.githubusercontent.com/imxtrabored/XanderBot/'
                 f'master/xanderbot/feh/data/heroes/{hero.index}/Face.png')
        )
        if bad_args:
            content = ('I did not understand the following arguments: '
                       f'{", ".join(bad_args)}')
        else:
            content = ''
        return ReplyPayload(content=content, embed=embed)
