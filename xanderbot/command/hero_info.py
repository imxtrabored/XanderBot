from dataclasses import dataclass

from discord import Embed

from command.cmd_default import CmdDefault
from command.common import (
    ReactMenu, UserPrompt, ReplyPayload, ReactEditPayload,
    format_hero_title, format_legend_eff, process_hero, process_hero_spaces,
)
from command.common_barracks import callback_save
from feh.currency import Dragonflower
from feh.emojilib import EmojiLib as em
from feh.hero import Hero, Rarity, Stat
from feh.interface import DragonflowerInc, RarityInc
from feh.skill import Skill
from feh.unitlib import UnitLib


class HeroInfo(CmdDefault):

    help_text = (
        'The ``hero`` command lists a hero\'s skills and attribute scores.\n\n'
        'Usage: ``f?hero {hero name}, {modifier 1}, {modifier 2}, {additional '
        'modifiers...}``\n\n'
        'Tip: Try adding skills to a hero to visualize that hero\'s potential '
        'in-game.\n'
        'For help on hero modifier syntax, use ``f?help syntax``.'
    )

    @dataclass
    class Data(object):

        __slots__ = ('embed', 'hero', 'zoom_state')

        embed: Embed
        hero: Hero
        zoom_state: bool

    @staticmethod
    def format_hero(hero, embed, zoom_state):
        title = format_hero_title(hero)
        desc_rarity = str(em.get(Rarity(hero.rarity))) * hero.rarity
        if hero.boon is not Stat.NONE and hero.bane is not Stat.NONE:
            if hero.merges == 0:
                ivs = f'\n(+{hero.boon.short}/-{hero.bane.short})'
            else:
                ivs = f'\n(+{hero.boon.short}/~~-{hero.bane.short}~~)'
        else:
            ivs = ''
        if zoom_state:
            if hero.is_legend:
                legend_desc = f'{format_legend_eff(hero)}\n'
            else:
                legend_desc = ''
            hero_desc = f'\n```{hero.description}```'
        else:
            legend_desc = ''
            hero_desc = ''
        desc_level = (
            f'{legend_desc}{desc_rarity} LV. {hero.level}+{hero.merges} · '
            f'{em.get(Dragonflower.get_move(hero.move_type))}+{hero.flowers}'
            f'{ivs}{hero_desc}'
        )
        """
        superboons = [
            '' if x == 0 else ' (+)' if x > 0 else ' (-)'
            for x in hero.get_boons_banes()
        ]
        """
        if any(hero.equipped):
            hero_stats = (hero.final_hp, hero.final_atk, hero.final_spd,
                          hero.final_def, hero.final_res)
            max_stats = (
                f'{em.get(Stat.HP)} HP: {hero_stats[0]}\n'
                f'{em.get(Stat.ATK)} Atk: {hero_stats[1]}\n'
                f'{em.get(Stat.SPD)} Spd: {hero_stats[2]}\n'
                f'{em.get(Stat.DEF)} Def: {hero_stats[3]}\n'
                f'{em.get(Stat.RES)} Res: {hero_stats[4]}\n\n'
                f'Total: {sum(hero_stats)}'
            )
            weapon = hero.equipped.weapon or Skill.EMPTY_WEAPON
            assist = hero.equipped.assist or Skill.EMPTY_ASSIST
            special = hero.equipped.special or Skill.EMPTY_SPECIAL
            passive_a = hero.equipped.passive_a or Skill.EMPTY_PASSIVE_A
            passive_b = hero.equipped.passive_b or Skill.EMPTY_PASSIVE_B
            passive_c = hero.equipped.passive_c or Skill.EMPTY_PASSIVE_C
            passive_s = hero.equipped.passive_s or Skill.EMPTY_PASSIVE_S
            stats_label = 'Stats'
            skills_label = 'Equipped Skills'
        else:
            superboons = [
                '' if x == 0 else ' (+)' if x > 0 else ' (-)'
                for x in hero.get_boons_banes()
            ]
            max_stats = (
                f'{em.get(Stat.HP)} HP: {hero.max_hp}{superboons[0]}\n'
                f'{em.get(Stat.ATK)} Atk: {hero.max_atk}{superboons[1]}\n'
                f'{em.get(Stat.SPD)} Spd: {hero.max_spd}{superboons[2]}\n'
                f'{em.get(Stat.DEF)} Def: {hero.max_def}{superboons[3]}\n'
                f'{em.get(Stat.RES)} Res: {hero.max_res}{superboons[4]}\n\n'
                f'Total: {hero.max_total}'
            )
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
            passive_s = None
            stats_label = 'Base Stats'
            skills_label = 'Learnable Skills'
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
            f'{special.icon} {it[2]}{special.name}{it[2]}\n'
            f'{passive_a.icon} {it[3]}{passive_a.name}{it[3]}\n'
            f'{passive_b.icon} {it[4]}{passive_b.name}{it[4]}\n'
            f'{passive_c.icon} {it[5]}{passive_c.name}{it[5]}\n'
            f'{passive_s.icon if passive_s else ""} '
            f'{passive_s.name if passive_s else ""}\n'
        )
        embed.clear_fields()
        embed.add_field(name=title, value=desc_level, inline=False)
        embed.add_field(name=stats_label, value=max_stats, inline=True)
        embed.add_field(name=skills_label, value=desc_skills, inline=True)
        if zoom_state:
            embed.add_field(
                name='Credits',
                value=f'\👄 {hero.vo_en}\n\🖋 {hero.artist}',
                inline=False
            )
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
                    emojis=react_emojis, callback=HeroInfo.react),
            )
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
                    ),
                    reactable=ReactMenu(react_emojis, None, HeroInfo.react),
                )
            embed.set_footer(
                text=('Please delimit modifiers with commas (,) '
                      'in the future to improve command processing.')
            )
        else:
            hero, bad_args = process_hero(hero, tokens[1:])
        embed = HeroInfo.format_hero(hero, embed, False)
        embed.set_thumbnail(
            url=('https://raw.githubusercontent.com/imxtrabored/XanderBot/'
                 f'master/xanderbot/feh/data/heroes/{hero.index}/Face.png')
        )
        if bad_args:
            content = ('I did not understand the following arguments: '
                       f'{", ".join(bad_args)}')
        else:
            content = None
        react_emojis[7] = em.get(DragonflowerInc.get_type(hero.move_type))
        react_menu = ReactMenu(
            emojis=react_emojis,
            data=HeroInfo.Data(embed, hero, False),
            callback=HeroInfo.react,
        )
        return ReplyPayload(content=content, embed=embed, reactable=react_menu)


    @staticmethod
    async def react(reaction, data, user_id):
        if not data:
            return ReactEditPayload(delete=True)
        if   reaction.emoji == '🔍':
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
                        icon_url=(
                            'https://emojipedia-us.s3.dualstack.us-west-1.'
                            'amazonaws.com/thumbs/120/google/146/'
                            'floppy-disk_1f4be.png'
                        )
                    )
                else:
                    data.embed.set_footer(
                        text='Error: Saved hero not found...',
                        icon_url=(
                            'https://emojipedia-us.s3.dualstack.us-west-1.'
                            'amazonaws.com/thumbs/120/google/146/'
                            'floppy-disk_1f4be.png'
                        )
                    )
            else:
                return ReactEditPayload(
                    delete=True,
                    replyable=UserPrompt(
                        callback=callback_save,
                        content='Enter a new name:',
                        data=data.hero
                    )
                )
        elif reaction.emoji == '👁':
            data.embed.set_author(name=str(data.hero.index))
        else:
            return ReactEditPayload()
        data.embed = HeroInfo.format_hero(
            data.hero, data.embed, data.zoom_state)
        return ReactEditPayload(embed=data.embed, delete=True)
