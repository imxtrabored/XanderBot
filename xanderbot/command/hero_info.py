import asyncio

import discord

from command.cmd_default import CmdDefault
from command.common import format_hero_title, process_hero, process_hero_spaces
from feh.emojilib import EmojiLib as em
from feh.hero import Rarity, Stat
from feh.skill import Skill, SkillType
from feh.unitlib import UnitLib


class HeroInfo(CmdDefault):

    help_text = (
        'The ``stats`` command lists a hero\'s attribute scores.\n\n'
        'Usage: ``f?stats {hero name}, {modifier 1}, {modifier 2}, {additional '
        'modifiers...}``'
    )

    @staticmethod
    def format_hero(hero, embed, zoom_state):
        title = format_hero_title(hero)

        desc_rarity = str(em.get(Rarity(hero.rarity))) * hero.rarity
        desc_level = f'LV. {hero.level}+{hero.merges}, DF: {hero.flowers}'
        """
        superboons = [
            '' if x == 0 else ' (+)' if x > 0 else ' (-)'
            for x in hero.get_boons_banes()
        ]
        """

        max_stats = (
            f'{em.get(Stat.HP)} HP: {hero.max_hp}\n'
            f'{em.get(Stat.ATK)} Atk: {hero.max_atk}\n'
            f'{em.get(Stat.SPD)} Spd: {hero.max_spd}\n'
            f'{em.get(Stat.DEF)} Def: {hero.max_def}\n'
            f'{em.get(Stat.RES)} Res: {hero.max_res}\n\n'
            f'Total: {hero.max_total}'
        )

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
            f'{weapon.icon} {weapon.name}\n'
            f'{assist.icon} {assist.name}\n'
            f'{special.icon} {special.name}\n'
            f'{passive_a.icon} {passive_a.name}\n'
            f'{passive_b.icon} {passive_b.name}\n'
            f'{passive_c.icon} {passive_c.name}\n'
        )

        embed.clear_fields()
        embed.add_field(name = title,
                        value = desc_rarity,
                        inline = False)
        embed.add_field(name = desc_level,
                        value = max_stats,
                        inline = True)
        embed.add_field(name = 'Skills',
                        value = desc_skills,
                        inline = True)
        embed.color = em.get_color(hero.color)
        return embed


    @staticmethod
    async def cmd(params):
        tokens = params.split(',')
        zoom_state = False
        if not tokens:
            return 'No input detected!', None, [None, False]
        hero = UnitLib.get_hero(tokens[0])
        embed = discord.Embed()
        if not hero:
            if ',' not in params: hero, bad_args = process_hero_spaces(params)
            if not hero:
                return (
                    f'Hero not found: {tokens[0]}. '
                    "Don't forget that modifiers should be delimited by commas.",
                    None, None
                )
            embed.set_author(
                name = 'Please delimit modifiers with commas (,) '
                'in the future to improve command processing.'
            )
        else:
            hero, bad_args = process_hero(hero, tokens[1:])
        embed = HeroInfo.format_hero(hero, embed, zoom_state)

        embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{hero.id}/Face.png')
        if bad_args:
            content = ('I did not understand the following arguments: '
                       f'{", ".join(bad_args)}')
        else:
            content = ''
        return content, embed, [hero, zoom_state]


    @staticmethod
    async def finalize(bot_reply, data):
        await bot_reply.add_reaction('🔍')
        await bot_reply.add_reaction(em.get(Rarity.ONE  ))
        await bot_reply.add_reaction(em.get(Rarity.TWO  ))
        await bot_reply.add_reaction(em.get(Rarity.THREE))
        await bot_reply.add_reaction(em.get(Rarity.FOUR ))
        await bot_reply.add_reaction(em.get(Rarity.FIVE ))
        await bot_reply.add_reaction('➖')
        await bot_reply.add_reaction('➕')
        await bot_reply.add_reaction('🔟')
        await bot_reply.add_reaction('🥀')
        await bot_reply.add_reaction('🌹')


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
        elif reaction.emoji == '➖':
            hero.update_stat_mods(merges = hero.merges - 1)
        elif reaction.emoji == '➕':
            hero.update_stat_mods(merges = hero.merges + 1)
        elif reaction.emoji == '🔟':
            hero.update_stat_mods(merges = 10)
        elif reaction.emoji == '🥀':
            hero.update_stat_mods(flowers = hero.flowers - 1)
        elif reaction.emoji == '🌹':
            hero.update_stat_mods(flowers = hero.flowers + 1)
        elif reaction.emoji == '💾':
            embed.set_footer(text = 'Coming Soon!',
                             icon_url = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/146/floppy-disk_1f4be.png')
        elif reaction.emoji == '👁':
            embed.set_author(name=str(hero.id))
        else: return None, None, False
        embed = HeroStats.format_stats(hero, embed, data[1])
        return None, embed, True
