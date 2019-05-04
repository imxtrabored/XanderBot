from dataclasses import dataclass

from discord import Embed

from command.cmd_default import CmdDefault
from command.common import (
    ReactMenu, UserPrompt, ReplyPayload, ReactEditPayload,
    format_hero_title, format_legend_eff, process_hero,
)
from feh.emojilib import EmojiLib as em
from feh.hero import Hero, Rarity
from feh.interface import RarityInc
from feh.skill import Skill, SkillType


class HeroSkills(CmdDefault):

    help_text = (
        'The ``skills`` command lists the skills that a hero can learn by '
        'default, without inheritance.\n\n'
        'Usage: ``f?skills {hero name}``\n\n'
        'Note: To display information on a specific skill, use the ``skill`` '
        '(without the s) command.'
    )

    @dataclass
    class Data(object):

        __slots__ = ('embed', 'hero', 'zoom_state')

        embed: Embed
        hero: Hero
        zoom_state: bool

    @staticmethod
    def format_hero_skills(embed, hero, zoom_state):
        title = format_hero_title(hero)
        desc_rarity = (str(em.get(Rarity(hero.rarity))) * hero.rarity
                       if not zoom_state else '-')
        desc_skills = ''
        if zoom_state:
            weapon = (
                [(f'{em.get(Rarity(skill[1]))} · '
                  f'{skill[0].icon} {skill[0].name}')
                 if not skill[0].exclusive else
                 (f'{em.get(Rarity(skill[1]))} · '
                  f'{skill[0].icon} _{skill[0].name}_')
                 for skill in hero.weapon]
                if hero.weapon else ('None',)
            )
            assist = (
                [(f'{em.get(Rarity(skill[1]))} · '
                  f'{skill[0].icon} {skill[0].name}')
                 if not skill[0].exclusive else
                 (f'{em.get(Rarity(skill[1]))} · '
                  f'{skill[0].icon} _{skill[0].name}_')
                 for skill in hero.assist]
                if hero.assist else ('None',)
            )
            special = (
                [(f'{em.get(Rarity(skill[1]))} · '
                  f'{skill[0].icon} {skill[0].name}')
                 if not skill[0].exclusive else
                 (f'{em.get(Rarity(skill[1]))} · '
                  f'{skill[0].icon} _{skill[0].name}_')
                 for skill in hero.special]
                if hero.special else ('None',)
            )
            passive_a = (
                [(f'{em.get(Rarity(skill[1]))} · '
                  f'{skill[0].icon} {skill[0].name}')
                 if not skill[0].exclusive else
                 (f'{em.get(Rarity(skill[1]))} · '
                  f'{skill[0].icon} _{skill[0].name}_')
                 for skill in hero.passive_a]
                if hero.passive_a else ('None',)
            )
            passive_b = (
                [(f'{em.get(Rarity(skill[1]))} · '
                  f'{skill[0].icon} {skill[0].name}')
                 if not skill[0].exclusive else
                 (f'{em.get(Rarity(skill[1]))} · '
                  f'{skill[0].icon} _{skill[0].name}_')
                 for skill in hero.passive_b]
                if hero.passive_b else ('None',)
            )
            passive_c = (
                [(f'{em.get(Rarity(skill[1]))} · '
                  f'{skill[0].icon} {skill[0].name}')
                 if not skill[0].exclusive else
                 (f'{em.get(Rarity(skill[1]))} · '
                  f'{skill[0].icon} _{skill[0].name}_')
                 for skill in hero.passive_c]
                if hero.passive_c else ('None',)
            )
        else:
            weapon = next((s[0] for s in hero.weapon[::-1]
                           if s[1] <= hero.rarity), Skill.EMPTY_WEAPON)
            assist = next((s[0] for s in hero.assist[::-1]
                           if s[1] <= hero.rarity), Skill.EMPTY_ASSIST)
            special = next((s[0] for s in hero.special[::-1]
                            if s[1] <= hero.rarity), Skill.EMPTY_SPECIAL)
            passive_a = next((s[0] for s in hero.passive_a[::-1]
                              if s[1] <= hero.rarity), Skill.EMPTY_PASSIVE_A)
            passive_b = next((s[0] for s in hero.passive_b[::-1]
                              if s[1] <= hero.rarity), Skill.EMPTY_PASSIVE_B)
            passive_c = next((s[0] for s in hero.passive_c[::-1]
                              if s[1] <= hero.rarity), Skill.EMPTY_PASSIVE_C)
            it = (
                '_' if weapon and weapon.exclusive else '',
                '_' if assist and assist.exclusive else '',
                '_' if special and special.exclusive else '',
                '_' if passive_a and passive_a.exclusive else '',
                '_' if passive_b and passive_b.exclusive else '',
                '_' if passive_c and passive_c.exclusive else '',
            )
            desc_skills = (
                f'{weapon.icon} {it[0]}{weapon.name}{it[0]}\n'
                f'{assist.icon} {it[1]}{assist.name}{it[1]}\n'
                f'{special.icon} {it[2]}{special.name}{it[2]}\n\n'
                f'{passive_a.icon}'
                f'{passive_a.skill_rank if passive_a.skill_rank > 0 else "-"}'
                f' · {passive_b.icon}'
                f'{passive_b.skill_rank if passive_b.skill_rank > 0 else "-"}'
                f' · {passive_c.icon}'
                f'{passive_c.skill_rank if passive_c.skill_rank > 0 else "-"}'
            )
        embed.clear_fields()
        description = f'{desc_rarity}\n\n{desc_skills}'
        embed.add_field(name=title, value=description, inline=False)
        if zoom_state:
            embed.add_field(name=f'{em.get(SkillType.WEAPON)} Weapon' ,
                            value='\n'.join(weapon), inline=True )
            embed.add_field(name=f'{em.get(SkillType.ASSIST)} '
                                 'Assist' ,
                            value='\n'.join(assist), inline=True )
            embed.add_field(name=f'{em.get(SkillType.SPECIAL  )} '
                                 'Special',
                            value='\n'.join(special), inline=False)
            embed.add_field(name=f'{em.get(SkillType.PASSIVE_A)} '
                                 'Passive',
                            value='\n'.join(passive_a), inline=True)
            embed.add_field(name=f'{em.get(SkillType.PASSIVE_B)} '
                                 'Passive',
                            value='\n'.join(passive_b), inline=True)
            embed.add_field(name=f'{em.get(SkillType.PASSIVE_C)} '
                                 'Passive',
                            value='\n'.join(passive_c), inline=False)
        embed.color = em.get_color(hero.color)
        return embed


    @staticmethod
    async def cmd(params, user_id):
        react_emojis = (
            '🔍',
            em.get(RarityInc.DOWN),
            em.get(RarityInc.UP),
        )
        if not params:
            return ReplyPayload(
                content='No input. Please enter a hero.',
                reactable=ReactMenu(
                    emojis=react_emojis, callback=HeroSkills.react),
            )
        hero, bad_args, not_allowed, no_commas = process_hero(params, user_id)
        if not hero:
            return ReplyPayload(
                content=(
                    f'Hero not found: {bad_args}. Don\'t forget that '
                    'modifiers should be delimited by commas.\n'
                    '(For information about a particular skill, use the '
                    '``skill`` (without an \'s\') command..)'
                ),
                reactable=ReactMenu(
                    react_emojis, None, HeroSkills.react),
            )
        embed = Embed()
        if no_commas:
            embed.set_footer(
                text=('Please delimit modifiers with commas (,) '
                      'in the future to improve command processing.')
            )
        embed = HeroSkills.format_hero_skills(embed, hero, False)
        err_text = []
        if any(bad_args):
            err_text.append('I did not understand the following: '
                            f'{", ".join(bad_args)}')
        if any(not_allowed):
            err_text.append('The following skills are unavailable for this '
                            f'hero: {", ".join(not_allowed)}')
        content = '\n'.join(err_text)
        embed.set_thumbnail(
            url=('https://raw.githubusercontent.com/imxtrabored/XanderBot/'
                 f'master/xanderbot/feh/data/heroes/{hero.index}/Face.png')
        )
        react_menu = ReactMenu(
            emojis=react_emojis,
            data=HeroSkills.Data(embed, hero, False),
            callback=HeroSkills.react,
        )
        return ReplyPayload(content=content, embed=embed, reactable=react_menu)

    @staticmethod
    async def react(reaction, data, user_id):
        if not data:
            return ReactEditPayload(delete=True)
        if reaction.emoji == '🔍':
            data.zoom_state = not data.zoom_state
        elif reaction.emoji == em.get(RarityInc.DOWN):
            rarity = data.hero.rarity
            data.hero.update_stat_mods(rarity=rarity - 1)
            if data.hero.rarity == rarity:
                return ReactEditPayload(delete=True)
        elif reaction.emoji == em.get(RarityInc.UP):
            rarity = data.hero.rarity
            data.hero.update_stat_mods(rarity=rarity + 1)
            if data.hero.rarity == rarity:
                return ReactEditPayload(delete=True)
        elif reaction.emoji == '👁':
            data.embed.set_author(name=str(hero.index))
        else:
            return ReactEditPayload()
        data.embed = HeroSkills.format_hero_skills(
            data.embed, data.hero, data.zoom_state)
        return ReactEditPayload(embed=data.embed, delete=True)
