import asyncio

import discord

from command.cmd_default import CmdDefault
from command.common import format_hero_title, process_hero, process_hero_spaces
from feh.emojilib import EmojiLib as em
from feh.hero import Rarity, Stat
from feh.unitlib import UnitLib


class HeroStats(CmdDefault):

    help_text = (
        'The ``stats`` command lists a hero\'s attribute scores.\n\n'
        'Usage: ``f?stats {hero name}, {modifier 1}, {modifier 2}, {additional '
        'modifiers...}``'
    )

    @staticmethod
    def format_stats(hero, embed, zoom_state):
        title = format_hero_title(hero)

        desc_rarity = str(em.get(Rarity(hero.rarity))) * hero.rarity
        desc_level = (f'{desc_rarity} LV. {hero.level}+{hero.merges}, '
                      f'DF: {hero.flowers}')
        desc_stat = ''
        if zoom_state:
            superboons = [
                '' if x == 0 else ' (+)' if x > 0 else ' (-)'
                for x in hero.get_boons_banes()
            ]
            lv1_stats = (
                f'{em.get(Stat.HP)} HP: '
                f'{hero.lv1_hp}\n'
                f'{em.get(Stat.ATK)} Attack: '
                f'{hero.lv1_atk}\n'
                f'{em.get(Stat.SPD)} Speed: '
                f'{hero.lv1_spd}\n'
                f'{em.get(Stat.DEF)} Defense: '
                f'{hero.lv1_def}\n'
                f'{em.get(Stat.RES)} Resistance: '
                f'{hero.lv1_res}\n\n'
                f'Total: {hero.lv1_total}'
            )
            max_stats = (
                f'{em.get(Stat.HP)} HP: '
                f'{hero.max_hp}{superboons[0]}\n'
                f'{em.get(Stat.ATK)} Attack: '
                f'{hero.max_atk}{superboons[1]}\n'
                f'{em.get(Stat.SPD)} Speed: '
                f'{hero.max_spd}{superboons[2]}\n'
                f'{em.get(Stat.DEF)} Defense: '
                f'{hero.max_def}{superboons[3]}\n'
                f'{em.get(Stat.RES)} Resistance: '
                f'{hero.max_res}{superboons[4]}\n\n'
                f'Total: {hero.max_total}'
            )
        else:
            stat_emojis = (
                f'{em.get(Stat.HP )} · '
                f'{em.get(Stat.ATK)} · '
                f'{em.get(Stat.SPD)} · '
                f'{em.get(Stat.DEF)} · '
                f'{em.get(Stat.RES)} · '
                f'BST: {hero.max_total}'
            )
            lvl1_stats = ' |'.join([
                f'{str(hero.lv1_hp ).rjust(2)} |'
                f'{str(hero.lv1_atk).rjust(2)} |'
                f'{str(hero.lv1_spd).rjust(2)} |'
                f'{str(hero.lv1_def).rjust(2)} |'
                f'{str(hero.lv1_res).rjust(2)}'
            ])
            superboons = [
                ' ' if x == 0 else '+' if x > 0 else '-'
                for x in hero.get_boons_banes()
            ]
            max_stats = ''.join([
                f'{str(hero.max_hp ).rjust(2)}{superboons[0]}|'
                f'{str(hero.max_atk).rjust(2)}{superboons[1]}|'
                f'{str(hero.max_spd).rjust(2)}{superboons[2]}|'
                f'{str(hero.max_def).rjust(2)}{superboons[3]}|'
                f'{str(hero.max_res).rjust(2)}{superboons[4]}'
            ])
            desc_stat = f'{stat_emojis}\n```\n{lvl1_stats}\n{max_stats}\n```'

        embed.clear_fields()
        description = f'{desc_level}\n\n{desc_stat}'
        embed.add_field(name = title,
                        value = description,
                        inline = False)

        if zoom_state:
            embed.add_field(name = 'Level 1 Stats',
                            value = lv1_stats,
                            inline = True)
            embed.add_field(name = 'Level 40 Stats',
                            value = max_stats,
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
        embed = HeroStats.format_stats(hero, embed, zoom_state)

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
