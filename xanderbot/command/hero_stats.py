from dataclasses import dataclass

from discord import Embed

from command.cmd_default import CmdDefault
from command.common import (
    ReactMenu, UserPrompt, ReplyPayload, ReactEditPayload,
    format_hero_title, format_legend_eff, process_hero,
)
from command.common_barracks import callback_save
from feh.currency import Dragonflower
from feh.emojilib import EmojiLib as em
from feh.hero import Hero, Rarity, Stat
from feh.interface import DragonflowerInc, RarityInc
from feh.unitlib import UnitLib


class HeroStats(CmdDefault):

    help_text = (
        'The ``stats`` command lists a hero\'s attribute scores.\n\n'
        'Usage: ``f?stats {hero name}, {modifier 1}, {modifier 2}, {additional '
        'modifiers...}``'
    )

    @dataclass
    class Data(object):

        __slots__ = ('embed', 'hero', 'zoom_state')

        embed: Embed
        hero: Hero
        zoom_state: bool


    @staticmethod
    def format_stats(embed, hero, zoom_state):
        title = format_hero_title(hero)
        desc_rarity = str(em.get(Rarity(hero.rarity))) * hero.rarity
        if hero.boon is not Stat.NONE and hero.bane is not Stat.NONE:
            if hero.merges == 0:
                ivs = f'(+{hero.boon.short}/-{hero.bane.short})\n'
            else:
                ivs = f'(+{hero.boon.short}/~~-{hero.bane.short}~~)\n'
        else:
            ivs = ''
        desc_level = (
            f'{desc_rarity} LV. {hero.level}+{hero.merges} · '
            f'{em.get(Dragonflower.get_move(hero.move_type))}+{hero.flowers}\n'
            f'{ivs}'
        )
        desc_stat = ''
        if any(hero.equipped):
            start_stats = (hero.start_hp, hero.start_atk, hero.start_spd,
                           hero.start_def, hero.start_res)
            final_stats = (hero.final_hp, hero.final_atk, hero.final_spd,
                           hero.final_def, hero.final_res)
            equipped = (
                '**Equipped:**\n'
                f'{"".join([str(sk.icon) for sk in hero.equipped])}'
            )
        else:
            start_stats = (hero.lv1_hp, hero.lv1_atk, hero.lv1_spd,
                           hero.lv1_def, hero.lv1_res)
            final_stats = (hero.max_hp, hero.max_atk, hero.max_spd,
                           hero.max_def, hero.max_res)
            equipped = ''
        if zoom_state:
            superboons = [
                '' if x == 0 else ' (+)' if x > 0 else ' (-)'
                for x in hero.get_boons_banes()
            ]
            lv1_stats = (
                f'{em.get(Stat.HP)} HP: '
                f'{start_stats[0]}\n'
                f'{em.get(Stat.ATK)} Attack: '
                f'{start_stats[1]}\n'
                f'{em.get(Stat.SPD)} Speed: '
                f'{start_stats[2]}\n'
                f'{em.get(Stat.DEF)} Defense: '
                f'{start_stats[3]}\n'
                f'{em.get(Stat.RES)} Resistance: '
                f'{start_stats[4]}\n\n'
                f'Total: {sum(start_stats)}'
            )
            max_stats = (
                f'{em.get(Stat.HP)} HP: '
                f'{final_stats[0]}{superboons[0]}\n'
                f'{em.get(Stat.ATK)} Attack: '
                f'{final_stats[1]}{superboons[1]}\n'
                f'{em.get(Stat.SPD)} Speed: '
                f'{final_stats[2]}{superboons[2]}\n'
                f'{em.get(Stat.DEF)} Defense: '
                f'{final_stats[3]}{superboons[3]}\n'
                f'{em.get(Stat.RES)} Resistance: '
                f'{final_stats[4]}{superboons[4]}\n\n'
                f'Total: {sum(final_stats)}'
            )
            description = (f'{desc_level}\n{equipped}')
        else:
            stat_emojis = (
                f'{em.get(Stat.HP )} · '
                f'{em.get(Stat.ATK)} · '
                f'{em.get(Stat.SPD)} · '
                f'{em.get(Stat.DEF)} · '
                f'{em.get(Stat.RES)} · '
                f'BST: {hero.max_total}'
            )
            lvl1_stats = (
                f'{start_stats[0]:2} |'
                f'{start_stats[1]:2} |'
                f'{start_stats[2]:2} |'
                f'{start_stats[3]:2} |'
                f'{start_stats[4]:2}'
            )
            superboons = [
                ' ' if x == 0 else '+' if x > 0 else '-'
                for x in hero.get_boons_banes()
            ]
            max_stats = (
                f'{final_stats[0]:2}{superboons[0]}|'
                f'{final_stats[1]:2}{superboons[1]}|'
                f'{final_stats[2]:2}{superboons[2]}|'
                f'{final_stats[3]:2}{superboons[3]}|'
                f'{final_stats[4]:2}{superboons[4]}'
            )
            desc_stat = (
                f'{stat_emojis}\n```\n{lvl1_stats}\n{max_stats}\n```{equipped}'
            )
            description = f'{desc_level}\n{desc_stat}'
        embed.clear_fields()
        embed.add_field(name=title, value=description, inline=False)
        if zoom_state:
            embed.add_field(name='Level 1 Stats', value=lv1_stats, inline=True)
            embed.add_field(name='Level 40 Stats', value=max_stats,
                            inline=True)
        embed.color = em.get_color(hero.color)
        return embed


    @staticmethod
    async def cmd(params, user_id):
        react_emojis = [
            '🔍',
            em.get(RarityInc.DOWN),
            em.get(RarityInc.UP),
            '➖',
            '➕',
            '🔟',
            em.get(DragonflowerInc.DOWN),
            em.get(DragonflowerInc.INFANTRY),
            '💾',
        ]
        if not params:
            return ReplyPayload(
                content='No input. Please enter a hero.',
                reactable=ReactMenu(
                    emojis=react_emojis, callback=HeroStats.react)
            )
        hero, bad_args, not_allowed, no_commas = process_hero(params, user_id)
        if not hero:
            return ReplyPayload(
                content=(
                    f'Hero not found: {bad_args}. Don\'t forget that '
                    'modifiers should be delimited by commas.'
                ),
                reactable=ReactMenu(
                    react_emojis, None, HeroStats.react),
            )
        embed = Embed()
        if no_commas:
            embed.set_footer(
                text=('Please delimit modifiers with commas (,) '
                      'in the future to improve command processing.')
            )
        embed = HeroStats.format_stats(embed, hero, False)
        embed.set_thumbnail(
            url=('https://raw.githubusercontent.com/imxtrabored/XanderBot/'
                 f'master/xanderbot/feh/data/heroes/{hero.index}/Face.png')
        )
        err_text = []
        if any(bad_args):
            err_text.append('I did not understand the following: '
                            f'{", ".join(bad_args)}')
        if any(not_allowed):
            err_text.append('The following are unavailable for this hero:'
                            f'{", ".join(not_allowed)}')
        content = '\n'.join(err_text)
        react_emojis[7] = em.get(DragonflowerInc.get_type(hero.move_type))
        react_menu = ReactMenu(
            emojis=react_emojis,
            data=HeroStats.Data(embed, hero, False),
            callback=HeroStats.react,
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
        elif reaction.emoji == '➖':
            merges = data.hero.merges
            data.hero.update_stat_mods(merges=merges - 1)
            if data.hero.merges == merges:
                return ReactEditPayload(delete=True)
        elif reaction.emoji == '➕':
            merges = data.hero.merges
            data.hero.update_stat_mods(merges=merges + 1)
            if data.hero.merges == merges:
                return ReactEditPayload(delete=True)
        elif reaction.emoji == '🔟':
            if data.hero.merges != 10:
                data.hero.update_stat_mods(merges=10)
            else:
                return ReactEditPayload(delete=True)
        elif reaction.emoji == em.get(DragonflowerInc.DOWN):
            flowers = data.hero.flowers
            data.hero.update_stat_mods(flowers=flowers - 1)
            if data.hero.flowers == flowers:
                return ReactEditPayload(delete=True)
        elif reaction.emoji in {
                em.get(DragonflowerInc.INFANTRY),
                em.get(DragonflowerInc.ARMOR   ),
                em.get(DragonflowerInc.CAVALRY ),
                em.get(DragonflowerInc.FLIER   ),
            }:
            flowers = data.hero.flowers
            data.hero.update_stat_mods(flowers=flowers + 1)
            if data.hero.flowers == flowers:
                return ReactEditPayload(delete=True)
        elif reaction.emoji == '💾':
            if data.hero.custom_name:
                if UnitLib.update_custom_hero(data.hero, user_id):
                    data.embed.set_footer(
                        text='Saved hero updated!',
                        icon_url='https://emojipedia-us.s3.dualstack.'
                        'us-west-1.amazonaws.com/thumbs/120/google/146/'
                        'floppy-disk_1f4be.png'
                    )
                else:
                    data.embed.set_footer(
                        text='Error: Saved hero not found...',
                        icon_url='https://emojipedia-us.s3.dualstack.'
                        'us-west-1.amazonaws.com/thumbs/120/google/146/'
                        'floppy-disk_1f4be.png'
                    )
            else:
                return ReactEditPayload(
                    delete=True,
                    replyable=UserPrompt(
                        callback=callback_save,
                        content=(
                            f'Enter a new name for custom {data.hero.name}:'),
                        data=data.hero
                    )
                )
        elif reaction.emoji == '👁':
            data.embed.set_author(name=str(data.hero.index))
        else:
            return ReactEditPayload()
        data.embed = HeroStats.format_stats(
            data.embed, data.hero, data.zoom_state)
        return ReactEditPayload(embed=data.embed, delete=True)

