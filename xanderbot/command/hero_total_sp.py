from discord import Embed

from command.cmd_default import CmdDefault
from command.common import ReplyPayload, format_hero_title, process_hero
from feh.emojilib import EmojiLib as em
from feh.skill import Skill

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
        hero, bad_args, not_allowed, no_commas = process_hero(params, user_id)
        if not hero:
            return ReplyPayload(
                content=(
                    f'Hero not found: {bad_args[0]}. Don\'t forget that '
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
                sp = skill.get_cumul_sp_hero_recur(hero=hero)
                total_sp += sp
                sp_rows.append(f'{skill.icon}: **{sp} SP** · {skill.name}')
            total_sp_text = f'Total SP: **{total_sp}**'
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
        err_text = []
        if any(bad_args):
            err_text.append('I did not understand the following: '
                            f'{", ".join(bad_args)}')
        if any(not_allowed):
            err_text.append('The following skills are unavailable for this '
                            f'hero: {", ".join(not_allowed)}')
        content = '\n'.join(err_text)
        return ReplyPayload(content=content, embed=embed)
