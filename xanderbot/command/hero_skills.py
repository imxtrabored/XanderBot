import discord

from command.cmd_default import CmdDefault
from command.common import format_hero_title, process_hero, process_hero_spaces
from feh.emojilib import EmojiLib as em
from feh.hero import Rarity
from feh.skill import Skill, SkillType
from feh.unitlib import UnitLib


class HeroSkills(CmdDefault):

    help_text = (
        'The ``skills`` command lists the skills that a hero can learn by '
        'default, without inheritance.\n\n'
        'Usage: ``f?skills {hero name}``\n\n'
        'Note: To display information on a specific skill, use the ``skill`` '
        '(without the s) command.'
    )

    @staticmethod
    def format_hero_skills(hero, embed, zoom_state):
        title = format_hero_title(hero)

        desc_rarity = (str(em.get(Rarity(hero.rarity))) * hero.rarity
                       if not zoom_state else '-')
        desc_skills = ''
        if zoom_state:
            weapon    = ([f'{em.get(Rarity(skill[1]))} · '
                          f'{skill[0].icon} '
                          f'{skill[0].name}'
                          for skill in hero.weapon   ]
                         if hero.weapon    else ('None',))
            assist    = ([f'{em.get(Rarity(skill[1]))} · '
                          f'{skill[0].icon} '
                          f'{skill[0].name}'
                          for skill in hero.assist   ]
                         if hero.assist    else ('None',))
            special   = ([f'{em.get(Rarity(skill[1]))} · '
                          f'{skill[0].icon} '
                          f'{skill[0].name}'
                          for skill in hero.special  ]
                          if hero.special   else ('None',))
            passive_a = ([f'{em.get(Rarity(skill[1]))} · '
                          f'{skill[0].icon} '
                          f'{skill[0].name}'
                          for skill in hero.passive_a]
                         if hero.passive_a else ('None',))
            passive_b = ([f'{em.get(Rarity(skill[1]))} · '
                          f'{skill[0].icon} '
                          f'{skill[0].name}'
                          for skill in hero.passive_b]
                         if hero.passive_b else ('None',))
            passive_c = ([f'{em.get(Rarity(skill[1]))} · '
                          f'{skill[0].icon} '
                          f'{skill[0].name}'
                          for skill in hero.passive_c]
                         if hero.passive_c else ('None',))

        else:
            weapon    = next((s[0] for s in hero.weapon   [::-1]
                              if s[1] <= hero.rarity), Skill.EMPTY_WEAPON )
            assist    = next((s[0] for s in hero.assist   [::-1]
                              if s[1] <= hero.rarity), Skill.EMPTY_ASSIST )
            special   = next((s[0] for s in hero.special  [::-1]
                              if s[1] <= hero.rarity), Skill.EMPTY_SPECIAL)
            passive_a = next((s[0] for s in hero.passive_a[::-1]
                              if s[1] <= hero.rarity), Skill.EMPTY_PASSIVE_A)
            passive_b = next((s[0] for s in hero.passive_b[::-1]
                              if s[1] <= hero.rarity), Skill.EMPTY_PASSIVE_B)
            passive_c = next((s[0] for s in hero.passive_c[::-1]
                              if s[1] <= hero.rarity), Skill.EMPTY_PASSIVE_C)
            desc_skills = (
                f'{em.get(SkillType.WEAPON )}{weapon .name}\n'
                f'{em.get(SkillType.ASSIST )}{assist .name}\n'
                f'{em.get(SkillType.SPECIAL)}{special.name}\n\n'
                f'{passive_a.icon}'
                f'{passive_a.skill_rank if passive_a.skill_rank > 0 else "-"} · '
                f'{passive_b.icon}'
                f'{passive_b.skill_rank if passive_b.skill_rank > 0 else "-"} · '
                f'{passive_c.icon}'
                f'{passive_c.skill_rank if passive_c.skill_rank > 0 else "-"}'
            )

        embed.clear_fields()
        description = f'{desc_rarity}\n\n{desc_skills}'
        embed.add_field(name = title, value = description, inline=False)

        if zoom_state:
            embed.add_field(name = f'{em.get(SkillType.WEAPON   )} '
                                   'Weapon' ,
                            value = '\n'.join(weapon   ), inline = True )
            embed.add_field(name = f'{em.get(SkillType.ASSIST   )} '
                                   'Assist' ,
                            value = '\n'.join(assist   ), inline = True )
            embed.add_field(name = f'{em.get(SkillType.SPECIAL  )} '
                                   'Special',
                            value = '\n'.join(special  ), inline = False)
            embed.add_field(name = f'{em.get(SkillType.PASSIVE_A)} '
                                   'Passive',
                            value = '\n'.join(passive_a), inline = True )
            embed.add_field(name = f'{em.get(SkillType.PASSIVE_B)} '
                                   'Passive',
                            value = '\n'.join(passive_b), inline = True )
            embed.add_field(name = f'{em.get(SkillType.PASSIVE_C)} '
                                   'Passive',
                            value = '\n'.join(passive_c), inline = False)
        embed.color = em.get_color(hero.color)
        return embed


    @staticmethod
    async def cmd(params):
        tokens = params.split(',')
        if not tokens:
            return 'No input detected!', None, [None, False]
        zoom_state = False
        hero = UnitLib.get_hero(tokens[0])
        embed = discord.Embed()
        if not hero:
            if ',' not in params: hero, bad_args = process_hero_spaces(params)
            if not hero:
                return (
                    f'Hero not found: {tokens[0]}. '
                    'Don\'t forget that modifiers should be delimited by commas.'
                    'Note: To display information on a specific skill, use the '
                    '``skill`` (without the s) command.',
                    None, None
                )
            embed.set_author(
                name = 'Please delimit modifiers with commas (,) '
                       'in the future to improve command processing.'
            )
        else:
            process_hero(hero, tokens[1:])
        embed = HeroSkills.format_hero_skills(hero, embed, zoom_state)

        embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{hero.id}/Face.png')

        return None, embed, [hero, zoom_state]


    @staticmethod
    async def finalize(bot_reply):
        await bot_reply.add_reaction('🔍')
        await bot_reply.add_reaction(em.get(Rarity.ONE  ))
        await bot_reply.add_reaction(em.get(Rarity.TWO  ))
        await bot_reply.add_reaction(em.get(Rarity.THREE))
        await bot_reply.add_reaction(em.get(Rarity.FOUR ))
        await bot_reply.add_reaction(em.get(Rarity.FIVE ))


    @staticmethod
    async def react(reaction, bot_msg, embed, data):
        hero = data[0]
        if   reaction.emoji == '🔍':
            data[1] = not data[1]
        elif reaction.emoji == em.get(Rarity.ONE  ):
            hero.update_stat_mods(rarity = 1)
        elif reaction.emoji == em.get(Rarity.TWO  ):
            hero.update_stat_mods(rarity = 2)
        elif reaction.emoji == em.get(Rarity.THREE):
            hero.update_stat_mods(rarity = 3)
        elif reaction.emoji == em.get(Rarity.FOUR ):
            hero.update_stat_mods(rarity = 4)
        elif reaction.emoji == em.get(Rarity.FIVE ):
            hero.update_stat_mods(rarity = 5)
        elif reaction.emoji == '💾':
            embed.set_footer(text = 'Coming Soon!',
                             icon_url = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/146/floppy-disk_1f4be.png')
        elif reaction.emoji == '👁':
            embed.set_author(name=str(hero.id))
        else: return None, None, False
        embed = HeroSkills.format_hero_skills(hero, embed, data[1])
        return None, embed, True
