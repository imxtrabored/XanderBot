import asyncio
import re

from collections import Counter
from functools import reduce
from operator import methodcaller
from string import punctuation, whitespace

import discord

from feh.emojilib import EmojiLib as em
from feh.hero import MoveType
from feh.hero import Stat, Rarity
from feh.skill import Skill, SkillType, SkillWeaponGroup
from feh.unitlib import UnitLib

TRANSTAB = str.maketrans('', '', punctuation + whitespace)
NON_DECIMAL = re.compile(r'[^\d]+')

class Command(object):
    """contains the commands that interact with feh data"""
    devs = []


    @staticmethod
    def filter_name(name):
        return name.lower().replace('+', 'plus').replace('-', 'minus').translate(TRANSTAB)



    @staticmethod
    async def do_nothing(*args, **kwargs):
        pass



    @staticmethod
    def process_hero_mods(hero, args):
        bad_args = []
        rarity = None
        merges = None
        boon = None
        bane = None
        level = None
        for token in args:
            param = Command.filter_name(token[:24])
            # rarity, merges, iv, level, "summoned"
            # regex might be faster or slower here idk
            rarity_test = (param.replace('*', '').replace('star', '')
                           .replace('rarity', ''))
            if rarity_test.isdecimal():
                rarity = int(rarity_test)
            elif 'plusplus' in param or 'futuremerge' in param:
                merges = int(NON_DECIMAL.sub('', param))
                hero.newmerges = True
            elif 'merge' in param:
                merges = int(NON_DECIMAL.sub('', param))
                hero.newmerges = False
            elif 'plus' in param:
                # this might be merges, iv, or a skill
                plus_test = param.replace('plus', '')
                if plus_test.isdecimal():
                    merges = int(plus_test)
                    hero.newmerges = False
                elif (
                        param in [
                            'plushp'       ,
                            'hpplus'       ,
                            'plushitpoint' ,
                            'plushitpoints',
                            'hitpointplus' ,
                            'hitpointsplus',
                        ]
                ):
                    boon = Stat.HP
                elif (
                        param in (
                            'plusatk'   ,
                            'atkplus'   ,
                            'plusattack',
                            'attackplus',
                        )
                ):
                    boon = Stat.ATK
                elif (
                        param in (
                            'plusspd'  ,
                            'spdplus'  ,
                            'plusspeed',
                            'speedplus',
                        )
                ):
                    boon = Stat.SPD
                elif (
                        param in (
                            'plusdef'    ,
                            'defplus'    ,
                            'plusdefense',
                            'defenseplus',
                            'plusdefence',
                            'defenceplus',
                        )
                ):
                    boon = Stat.DEF
                elif (
                        param in (
                            'plusres'       ,
                            'resplus'       ,
                            'plusresistance',
                            'resistanceplus',
                        )
                ):
                    boon = Stat.RES
                else:
                    skill = UnitLib.get_skill(param)
                    if skill:
                        if skill.type == SkillType.WEAPON:
                            hero.equipped_weapon = skill
                        elif skill.type == SkillType.ASSIST:
                            hero.equipped_assist = skill
                        elif skill.type == SkillType.SPECIAL:
                            hero.equipped_special = skill
                        elif skill.type == SkillType.PASSIVE_A:
                            if (hero.equipped_passive_a
                                and not hero.equipped_passive_s
                                and skill.is_seal):
                                hero.equipped_passive_s = skill
                            else: hero.equipped_passive_a = skill
                        elif skill.type == SkillType.PASSIVE_B:
                            if (hero.equipped_passive_b
                                and not hero.equipped_passive_s
                                and skill.is_seal):
                                hero.equipped_passive_s = skill
                            else: hero.equipped_passive_b = skill
                        elif skill.type == SkillType.PASSIVE_C:
                            if (hero.equipped_passive_c
                                and not hero.equipped_passive_s
                                and skill.is_seal):
                                hero.equipped_passive_s = skill
                            else: hero.equipped_passive_c = skill
                        elif skill.type == SkillType.PASSIVE_SEAL:
                            hero.equipped_passive_s = skill
                    else:
                        bad_args.append(token)
            elif 'boon' in param or 'asset' in param:
                if 'hp' in param or 'hitpoint' in param:
                    boon = Stat.HP
                elif 'atk' in param or 'attack' in param:
                    boon = Stat.ATK
                elif 'spd' in param or 'speed' in param:
                    boon = Stat.SPD
                elif 'def' in param:
                    boon = Stat.DEF
                elif 'res' in param:
                    boon = Stat.RES
            elif 'minus' in param or 'bane' in param or 'flaw' in param:
                if 'hp' in param or 'hitpoint' in param:
                    bane = Stat.HP
                elif 'atk' in param or 'attack' in param:
                    bane = Stat.ATK
                elif 'spd' in param or 'speed' in param:
                    bane = Stat.SPD
                elif 'def' in param:
                    bane = Stat.DEF
                elif 'res' in param:
                    bane = Stat.RES
            else:
                skill = UnitLib.get_skill(param)
                if skill:
                    if skill.type == SkillType.WEAPON:
                        hero.equipped_weapon = skill
                    elif skill.type == SkillType.ASSIST:
                        hero.equipped_assist = skill
                    elif skill.type == SkillType.SPECIAL:
                        hero.equipped_special = skill
                    elif skill.type == SkillType.PASSIVE_A:
                        if (hero.equipped_passive_a
                            and not hero.equipped_passive_s
                            and skill.is_seal):
                            hero.equipped_passive_s = skill
                        else: hero.equipped_passive_a = skill
                    elif skill.type == SkillType.PASSIVE_B:
                        if (hero.equipped_passive_b
                            and not hero.equipped_passive_s
                            and skill.is_seal):
                            hero.equipped_passive_s = skill
                        else: hero.equipped_passive_b = skill
                    elif skill.type == SkillType.PASSIVE_C:
                        if (hero.equipped_passive_c
                            and not hero.equipped_passive_s
                            and skill.is_seal):
                            hero.equipped_passive_s = skill
                        else: hero.equipped_passive_c = skill
                    elif skill.type == SkillType.PASSIVE_SEAL:
                        hero.equipped_passive_s = skill
                else:
                    bad_args.append(token)

        if   boon is None and bane is not None:
            bane = None
            bad_args.append(f'\n{hero.short_name} has flaw but no asset; ignoring flaw')
        elif boon is not None and bane is None:
            if boon != Stat.HP:
                bane = Stat.HP
                bad_args.append(f'\n{hero.short_name} has no flaw; defaulting to HP flaw')
            else:
                bane = Stat.ATK
                bad_args.append(f'\n{hero.short_name} has no flaw; defaulting to Atk flaw')

        hero.update_stat_mods(boon = boon, bane = bane, merges = merges,
                              rarity = rarity)

        return hero, bad_args



    @staticmethod
    async def cmd_hero(params):
        return 'Not implemented yet!', None, None



    @staticmethod
    async def finalize_hero(bot_reply):
        return



    @staticmethod
    async def react_hero(reaction, bot_msg, embed, data):
        return



    @staticmethod
    def format_stats(hero, embed, zoom_state):
        if hero.is_legend:
            legend_info = (f'{em.get(hero.legend_element)}'
                           f'{em.get(hero.legend_boost)}'
                           )
        else: legend_info = ''
        title = (f'{hero.name}: {hero.epithet} '
                 f'{em.get(hero.weapon_type)}'
                 f'{em.get(hero.move_type)}'
                 f'{legend_info}'
                 )

        desc_rarity = str(em.get(Rarity(hero.rarity))) * hero.rarity
        desc_level = f'{desc_rarity} LV. {hero.level}+{hero.merges}'
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
        return embed



    @staticmethod
    async def cmd_stats(params):
        tokens = params.split(',')
        zoom_state = False
        if not tokens:
            return 'No input detected!', None, None
        hero = UnitLib.get_hero(tokens[0])
        if not hero:
            return (f'Hero not found: {tokens[0]}. '
                    "Don't forget that modifiers should be delimited by commas.",
                    None, None)
        hero, bad_args = Command.process_hero_mods(hero, tokens[1:])
        embed = discord.Embed()
        embed = Command.format_stats(hero, embed, zoom_state)

        embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{hero.id}/Face.png')
        if bad_args:
            content = ('I did not understand the following arguments: '
                       f'{", ".join(bad_args)}')
        else:
            content = ''
        return content, embed, [hero, zoom_state]



    @staticmethod
    async def finalize_stats(bot_reply):
        await bot_reply.add_reaction('🔍')
        await bot_reply.add_reaction(em.get(Rarity.ONE  ))
        await bot_reply.add_reaction(em.get(Rarity.TWO  ))
        await bot_reply.add_reaction(em.get(Rarity.THREE))
        await bot_reply.add_reaction(em.get(Rarity.FOUR ))
        await bot_reply.add_reaction(em.get(Rarity.FIVE ))
        await bot_reply.add_reaction('➕')
        await bot_reply.add_reaction('➖')
        await bot_reply.add_reaction('🔟')



    @staticmethod
    async def react_stats(reaction, bot_msg, embed, data):
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
        elif reaction.emoji == '➕':
            hero.update_stat_mods(merges = hero.merges + 1)
        elif reaction.emoji == '➖':
            hero.update_stat_mods(merges = hero.merges - 1)
        elif reaction.emoji == '🔟':
            hero.update_stat_mods(merges = 10)
        elif reaction.emoji == '⏩':
            hero.newmerges = True
            hero.update_stat_mods(merges = hero.merges)
            asyncio.create_task(bot_msg.add_reaction('⏪'))
            asyncio.create_task(bot_msg.add_reaction('⏩'))
        elif reaction.emoji == '⏪':
            hero.newmerges = False
            hero.update_stat_mods(merges = hero.merges)
            asyncio.create_task(bot_msg.add_reaction('⏪'))
            asyncio.create_task(bot_msg.add_reaction('⏩'))
        elif reaction.emoji == '💾':
            embed.set_footer(text = 'Coming Soon!',
                             icon_url = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/146/floppy-disk_1f4be.png')
        elif reaction.emoji == '👁':
            embed.set_author(name=str(hero.id))
        else: return None, None, False
        embed = Command.format_stats(hero, embed, data[1])
        return None, embed, True



    @staticmethod
    def format_hero_skills(hero, embed, zoom_state):
        if hero.is_legend:
            legend_info = (f'{em.get(hero.legend_element)}'
                           f'{em.get(hero.legend_boost)}'
                           )
        else: legend_info = ''

        title = (
            f'{hero.name}: {hero.epithet} '
            f'{em.get(hero.weapon_type)}'
            f'{em.get(hero.move_type)}'
            f'{legend_info}'
        )

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
        return embed



    @staticmethod
    async def cmd_hskills(params):
        tokens = params.split(',')
        if not tokens:
            return 'No input detected!', None, None
        zoom_state = False
        hero = UnitLib.get_hero(tokens[0])
        if not hero:
            return (
                f'Hero not found: {tokens[0]}. '
                "Don't forget that modifiers should be delimited by commas.",
                None, None
            )
        Command.process_hero_mods(hero, tokens[1:])
        hero_embed = discord.Embed()
        hero_embed = Command.format_hero_skills(hero, hero_embed, zoom_state)

        hero_embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{hero.id}/Face.png')

        return None, hero_embed, [hero, zoom_state]



    @staticmethod
    async def finalize_hskills(bot_reply):
        await bot_reply.add_reaction('🔍')
        await bot_reply.add_reaction(em.get(Rarity.ONE  ))
        await bot_reply.add_reaction(em.get(Rarity.TWO  ))
        await bot_reply.add_reaction(em.get(Rarity.THREE))
        await bot_reply.add_reaction(em.get(Rarity.FOUR ))
        await bot_reply.add_reaction(em.get(Rarity.FIVE ))



    @staticmethod
    async def react_hskills(reaction, bot_msg, embed, data):
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
        embed = Command.format_hero_skills(hero, embed, data[1])
        return None, embed, True



    @staticmethod
    def format_compare(heroes, embed, zoom_state):
        embed.clear_fields()
        if not heroes:
            embed.description = 'No heroes found.'
            return embed
        elif len(heroes) == 1:
            embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{heroes[0].id}/Face.png')
            return Command.format_stats(heroes[0], embed, zoom_state)
        elif len(heroes) == 2:
            title = (f'Comparing {heroes[0].short_name} '
                     f'and {heroes[1].short_name}:')
        else:
            title = f'Comparing {", ".join([h.short_name for h in heroes])}:'

        embed.add_field(
            name = title,
            value = '-',
            inline = False
        )

        for hero in heroes:
            superboons = [
                '' if x == 0 else ' (+)' if x > 0 else ' (-)'
                for x in hero.get_boons_banes()
            ]
            max_stats = (
                f'{hero.rarity}{em.get(Rarity(hero.rarity))} '
                f'LV. {hero.level}+{hero.merges}\n'
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
                f'BST: {hero.max_total}'
            )

            embed.add_field(
                name = (
                    f'{hero.short_name} '
                    f'{em.get(hero.weapon_type)} '
                    f'{em.get(hero.move_type)} '
                ),
                value = max_stats,
                inline = True
            )

        if len(heroes) == 2:
            stat_sort = sorted(heroes,
                               key = lambda h: h.max_hp,
                               reverse = True)
            if stat_sort[0].max_hp > stat_sort[-1].max_hp:
                hp_str = (
                    f'{em.get(Stat.HP)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_hp - stat_sort[1].max_hp} '
                    'more HP.'
                )
            else: hp_str = f'{em.get(Stat.HP)} Equal HP'

            stat_sort = sorted(heroes,
                               key = lambda h: h.max_atk,
                               reverse = True)
            if stat_sort[0].max_atk > stat_sort[-1].max_atk:
                atk_str = (
                    f'{em.get(Stat.ATK)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_atk - stat_sort[1].max_atk} '
                    'more Attack.'
                )
            else: atk_str = f'{em.get(Stat.ATK)} Equal Attack.'

            stat_sort = sorted(heroes,
                               key = lambda h: h.max_spd,
                               reverse = True)
            if stat_sort[0].max_spd > stat_sort[-1].max_spd:
                spd_str = (
                    f'{em.get(Stat.SPD)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_spd - stat_sort[1].max_spd} '
                    'more Speed.'
                )
            else: spd_str = f'{em.get(Stat.SPD)} Equal Speed.'

            stat_sort = sorted(heroes,
                               key = lambda h: h.max_def,
                               reverse = True)
            if stat_sort[0].max_def > stat_sort[-1].max_def:
                def_str = (
                    f'{em.get(Stat.DEF)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_def - stat_sort[1].max_def} '
                    'more Defense.'
                )
            else: def_str = f'{em.get(Stat.DEF)} Equal Defense.'

            stat_sort = sorted(heroes,
                               key = lambda h: h.max_res,
                               reverse = True)
            if stat_sort[0].max_res > stat_sort[-1].max_res:
                res_str = (
                    f'{em.get(Stat.RES)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_res - stat_sort[1].max_res} '
                    'more Resistance.'
                )
            else: res_str = f'{em.get(Stat.RES)} Equal Resistance.'

            stat_sort = sorted(heroes,
                               key = lambda h: h.max_total,
                               reverse = True)
            if stat_sort[0].max_total > stat_sort[1].max_total:
                total_str = (
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_total - stat_sort[1].max_total} '
                    'more total stats.'
                )
            else: total_str = 'Equal stat total.'

        else:
            stat_sort = sorted(heroes,
                               key = lambda h: h.max_hp,
                               reverse = True)
            if stat_sort[0].max_hp > stat_sort[-1].max_hp:
                max_list = ", ".join([
                    h.short_name for h in heroes
                    if h.max_hp == stat_sort[0].max_hp])
                hp_str = (
                    f'{em.get(Stat.HP)} '
                    f'Greatest HP: {stat_sort[0].max_hp} '
                    f'({max_list})'
                )
            else: hp_str = (f'{em.get(Stat.HP)} '
                            'All heroes have equal HP.')

            stat_sort = sorted(heroes,
                               key = lambda h: h.max_atk,
                               reverse = True)
            if stat_sort[0].max_atk > stat_sort[-1].max_atk:
                max_list = ", ".join([
                    h.short_name for h in heroes
                    if h.max_atk == stat_sort[0].max_atk])
                atk_str = (
                    f'{em.get(Stat.ATK)} '
                    f'Greatest Attack: {stat_sort[0].max_atk} '
                    f'({max_list})'
                )
            else: atk_str = (f'{em.get(Stat.ATK)} '
                             'All heroes have equal Attack.')

            stat_sort = sorted(heroes,
                               key = lambda h: h.max_spd,
                               reverse = True)
            if stat_sort[0].max_spd > stat_sort[-1].max_spd:
                max_list = ", ".join([
                    h.short_name for h in heroes
                    if h.max_spd == stat_sort[0].max_spd])
                spd_str = (
                    f'{em.get(Stat.SPD)} '
                    f'Greatest Speed: {stat_sort[0].max_spd} '
                    f'({max_list})'
                )
            else: spd_str = (f'{em.get(Stat.SPD)} '
                             'All heroes have equal Speed.')

            stat_sort = sorted(heroes,
                               key = lambda h: h.max_def,
                               reverse = True)
            if stat_sort[0].max_def > stat_sort[-1].max_def:
                max_list = ", ".join([
                    h.short_name for h in heroes
                    if h.max_def == stat_sort[0].max_def])
                def_str = (
                    f'{em.get(Stat.DEF)} '
                    f'Greatest Defense: {stat_sort[0].max_def} '
                    f'({max_list})'
                )
            else: def_str = (f'{em.get(Stat.DEF)} '
                             'All heroes have equal Defense.')

            stat_sort = sorted(heroes,
                               key = lambda h: h.max_res,
                               reverse = True)
            if stat_sort[0].max_res > stat_sort[-1].max_res:
                max_list = ", ".join([
                    h.short_name for h in heroes
                    if h.max_res == stat_sort[0].max_res])
                res_str = (
                    f'{em.get(Stat.RES)} '
                    f'Greatest Resistance: {stat_sort[0].max_res} '
                    f'({max_list})'
                )
            else: res_str = (f'{em.get(Stat.RES)} '
                             'All heroes have equal Resistance.')

            stat_sort = sorted(heroes,
                               key = lambda h: h.max_total,
                               reverse = True)
            if stat_sort[0].max_total > stat_sort[-1].max_total:
                max_list = ", ".join([
                    h.short_name for h in heroes
                    if h.max_total == stat_sort[0].max_total])
                total_str = (
                    f'Greatest stat total: {stat_sort[0].max_total} '
                    f'({max_list})'
                )
            else: total_str = 'All heroes have equal stat totals.'

        embed.add_field(
            name = 'Analysis:',
            value = (f'{hp_str}\n{atk_str}\n{spd_str}\n'
                     f'{def_str}\n{res_str}\n\n{total_str}'),
            inline = True
        )
        return embed



    @staticmethod
    async def cmd_compare(params):
        if not params:
            return 'No input detected!', None, None
        zoom_state = False
        embed = discord.Embed()
        bad_args = []
        if ';' not in params:
            # slow mode
            params = params.split(',')
            heroes = []
            for param in params:
                this_hero = UnitLib.get_hero(param)
                if this_hero: heroes.append(this_hero)
                else:
                    if not heroes:
                        bad_args.append(param)
                    else:
                        heroes[-1], bad_arg = Command.process_hero_mods(heroes[-1], [param])
                        bad_args.extend(bad_arg)

            embed.set_author(
                name = ('Please delimit compared heroes with semicolons (;) '
                        'in the future to improve speed and clarity.')
            )
            # hero_embed = self.format_stats(this_hero, hero_embed, zoom_state)
        else:
            # normal mode
            hero_list = map(methodcaller('split', ','), params.split(';'))
            heroes = []
            for param in hero_list:
                this_hero = UnitLib.get_hero(param[0])
                if this_hero:
                    this_hero, bad_arg = Command.process_hero_mods(this_hero, param[1:])
                    heroes.append(this_hero)
                    bad_args.extend(bad_arg)
                else: bad_args.append(param[0])
        # modify duplicate hero names (detect dupes using id)
        counts = {k:v for k, v in
                  Counter([h.id for h in heroes]).items()
                  if v > 1}
        for i in reversed(range(len(heroes))):
            item = heroes[i].id
            if item in counts and counts[item]:
                heroes[i].short_name = (f'{heroes[i].short_name} '
                                        f'({counts[item]})')
                counts[item] -= 1
        embed = Command.format_compare(heroes, embed, zoom_state)

        if bad_args:
            content = ( 'I did not understand the following arguments: '
                       f'{", ".join(bad_args)}')
        else:
            content = ''
        return content, embed, [heroes, zoom_state]



    @staticmethod
    async def finalize_compare(bot_reply):
        return



    @staticmethod
    async def react_compare(reaction, bot_msg, embed, data):
        return None, None, False



    @staticmethod
    async def cmd_alts(params):
        tokens = params.split(',')
        if not tokens:
            return 'No input detected!', None, None
        zoom_state = False
        hero = UnitLib.get_hero(tokens[0])
        if not hero: return f'Hero not found: {tokens[0]}.', None, None
        embed = discord.Embed()
        embed.title = f'Heroes that are versions of {hero.alt_base.short_name}:'
        embed.description = '\n'.join([
            f'{em.get(alt.weapon_type)}{em.get(alt.move_type)} '
            f'{alt.name}: {alt.epithet} [{alt.short_name}]'
            for alt in hero.alt_base.alt_list
        ])

        embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{hero.id}/Face.png')

        return None, embed, [hero, zoom_state]



    @staticmethod
    async def finalize_alts(bot_reply):
        return



    @staticmethod
    async def react_alts(reaction, bot_msg, embed, data):
        return



    @staticmethod
    async def cmd_merges(params):
        tokens = params.split(',')
        if not tokens:
            return 'No input detected!', None, None
        zoom_state = False
        hero = UnitLib.get_hero(tokens[0])
        if not hero: return f'Hero not found: {tokens[0]}.', None, None
        embed = discord.Embed()
        hero, bad_args = Command.process_hero_mods(hero, tokens[1:])
        if hero.is_legend:
            legend_info = (f'{em.get(hero.legend_element)}'
                           f'{em.get(hero.legend_boost)}'
                           )
        else: legend_info = ''
        title = (f'{hero.name}: {hero.epithet} '
                 f'{em.get(hero.weapon_type)}'
                 f'{em.get(hero.move_type)}'
                 f'{legend_info}\nMerges:'
                 )
        bonuses = '\n'.join([
            f'{f"+{merges}".rjust(3)}:{"|".join([str(stat).rjust(3) for stat in row])}'
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
            f'```{bonuses}```'
        )
        embed.add_field(name = title, value = description, inline = True)
        if bad_args:
            content = ('I did not understand the following arguments: '
                       f'{", ".join(bad_args)}')
        else: content = ''

        embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{hero.id}/Face.png')

        return content, embed, [hero, zoom_state]



    @staticmethod
    async def finalize_merges(bot_reply):
        return



    @staticmethod
    async def react_merges(reaction, bot_msg, embed, data):
        return


    @staticmethod
    def format_eff(skill):
        if any((
                skill.eff_infantry,
                skill.eff_armor   ,
                skill.eff_cavalry ,
                skill.eff_flier   ,
                skill.eff_magic   ,
                skill.eff_dragon  ,
        )):
            eff_list = [' Eff: ']
            if skill.eff_infantry: eff_list.append(str(em.get(MoveType.INFANTRY)))
            if skill.eff_armor   : eff_list.append(str(em.get(MoveType.ARMOR   )))
            if skill.eff_cavalry : eff_list.append(str(em.get(MoveType.CAVALRY )))
            if skill.eff_flier   : eff_list.append(str(em.get(MoveType.FLIER   )))
            if skill.eff_magic   :
                eff_list.append(str(em.get(SkillWeaponGroup.R_TOME)))
                eff_list.append(str(em.get(SkillWeaponGroup.B_TOME)))
                eff_list.append(str(em.get(SkillWeaponGroup.G_TOME)))
            if skill.eff_dragon  : eff_list.append(str(em.get(SkillWeaponGroup.S_BREATH)))
            effective = ''.join(eff_list)
        else: effective = ''
        return effective



    @staticmethod
    def format_skill(skill, embed, zoom_state):
        type_icon = (em.get(skill.weapon_type)
                     if skill.weapon_type else em.get(skill.type))
        seal_icon = (em.get(SkillType.PASSIVE_SEAL)
                     if skill.type != SkillType.PASSIVE_SEAL and skill.is_seal
                     else "")
        title = f'{skill.icon} {skill.name} · {type_icon}{seal_icon}'

        if (skill.type == SkillType.WEAPON
            or skill.type == SkillType.WEAPON_REFINED
            ):
            effective = Command.format_eff(skill)

            weapon_desc = f'Mt: {skill.disp_atk} Rng: {skill.range}{effective}'
        elif skill.type == SkillType.SPECIAL:
            weapon_desc = f'{em.get(SkillType.SPECIAL)} {skill.special_cd}'
        else: weapon_desc = None

        prereq = (
            '_This skill can only be equipped by its original unit._'
            if skill.exclusive else
            f'**Requires:** {skill.prereq1.icon} {skill.prereq1.name} '
            f'or {skill.prereq2.icon} {skill.prereq2.name}'
            if skill.prereq2 else
            f'**Requires:** {skill.prereq1.icon} {skill.prereq1.name}'
            if skill.prereq1
            else None
        )

        if skill.type != SkillType.WEAPON and skill.type != SkillType.WEAPON_REFINED:
            if skill.is_staff:
                restrictions = "_This skill can only be equipped by staff users._"
            else:
                restrict_list = [em.restrict_emojis[count]
                                 for count, value in enumerate(skill.allowed)
                                 if not value]
                if restrict_list:
                    restrictions = f'**Cannot use:** {"".join(restrict_list)}'
                else: restrictions = None
        else: restrictions = None

        sp = f'**SP:** {skill.sp}'

        learnable_count = (len(skill.learnable[1]) + len(skill.learnable[2])
                           + len(skill.learnable[3]) + len(skill.learnable[4])
                           + len(skill.learnable[5]))
        if (skill.type == SkillType.WEAPON and not skill.exclusive
            and ((skill.tier <= 2 and not skill.is_staff) or skill.tier <= 1)):
            learnable = 'Basic weapon available to most eligible heroes.'
        elif (skill.type == SkillType.ASSIST and skill.is_staff
              and skill.tier <= 1):
            learnable = 'Basic assist available to all staff users.'
        # elif reduce(lambda x, y: x + len(y), skill.learnable[1:], 0) > 20:
        elif learnable_count > 20:
            learnable = 'Over 20 heroes know this skill.'
        elif learnable_count == 0:
            learnable = 'None'
        else:
            learnable = '\n'.join([
                f'{count}{em.get(Rarity(count))}: '
                f'{", ".join([hero.short_name for hero in hero_list])}'
                for count, hero_list in enumerate(skill.learnable[1:], 1)
                if hero_list
            ])

        embed.clear_fields()
        if zoom_state:
            if skill.postreq:
                prf_postreq_count = reduce(
                    lambda x, y: x + 1 if y.exclusive else x,
                    skill.postreq,
                    0
                )
                # optimize note?
                postreq_list = (', '.join([
                    f'{postreq.icon} {postreq.name}'
                    for postreq in skill.postreq
                    if not postreq.exclusive
                ])
                if len(skill.postreq) - prf_postreq_count < 10
                else ', '.join([
                    f'{postreq.name}'
                    for postreq in skill.postreq
                    if not postreq.exclusive
                ]))

                prf_postreqs = (f' and {prf_postreq_count} Prf skills.'
                                if prf_postreq_count else '')
            else:
                postreq_list = 'None'
                prf_postreqs = ''

            postreqs = f'**Required for:** {postreq_list}{prf_postreqs}'

            cumul_sp = f'**Cumulative SP:** {skill.get_cumul_sp_recursive()}'
            if skill.evolves_from:
                evolve_src = (
                    f'**Evolves from:** '
                    f'{skill.evolves_from.icon} {skill.evolves_from.name}')
            else: evolve_src = None
        else:
            postreqs, cumul_sp, evolve_src = None, None, None

        description = '\n'.join(filter(None, [
            weapon_desc,
            skill.description,
            prereq,
            restrictions,
            sp,
            cumul_sp,
            '**Available from:**',
            learnable,
            evolve_src,
            postreqs,
        ]))

        embed.add_field(
            name = title,
            value = description,
            inline = False
        )

        if skill.refinable or skill.evolves_to:
            if zoom_state:
                refine_secondary = (
                    f', {skill.refine_stones} '
                    f'{em.get("Currency_Refining_Stone")}'
                    if skill.refine_stones else
                    f', {skill.refine_dew} '
                    f'{em.get("Currency_Divine_Dew")}'
                    if skill.refine_dew else ''
                )
                refine_cost = (
                    f' {skill.refine_sp} SP, '
                    f'{skill.refine_medals} '
                    f'{em.get("Currency_Arena_Medal")}'
                    f'{refine_secondary}'
                )
            else: refine_cost = ''

            refine_header = (f'**Refine options:**{refine_cost}'
                             if skill.refinable else None)
            if skill.refined_version:
                refined_skill = skill.refined_version
                refined_title = (f'Weapon Refinery\n{refined_skill.icon} '
                                 f'Refined {skill.name} · {type_icon}'
                                 )
                effective = Command.format_eff(refined_skill)
                refined_w_desc = (
                    f'Mt: {refined_skill.disp_atk} '
                    f'Rng: {refined_skill.range}{effective}'
                    if (refined_skill.type == SkillType.WEAPON
                        or refined_skill.type == SkillType.WEAPON_REFINED
                        )
                    else None
                )
                refined_skill_str = '\n'.join(filter(None, (
                    refined_w_desc, refined_skill.description
                )))
            else:
                refined_title = 'Weapon Refinery'
                refined_skill_str = None

            refine_eff = (f'{skill.refine_eff.icon}: '
                          f'{skill.refine_eff.description}'
                          if skill.refine_eff else None)
            skill_refines = (
                skill.refine_staff1,
                skill.refine_staff2,
                skill.refine_atk,
                skill.refine_spd,
                skill.refine_def,
                skill.refine_res
            )
            if zoom_state:
                generic_refines = '\n'.join([
                    f'{refine.icon}: {refine.description}'
                    for refine in skill_refines
                    if refine
                ])
            else:
                generic_refines = ', '.join([
                    str(refine.icon)
                    for refine in skill_refines
                    if refine
                ])

            if zoom_state and skill.evolves_to:
                evolve_secondary = (
                    f', {skill.evolve_stones} '
                    f'{em.get("Currency_Refining_Stone")}'
                    if skill.evolve_stones else
                    f', {skill.evolve_dew} '
                    f'{em.get("Currency_Divine_Dew")}'
                    if skill.evolve_dew else ''
                )
                evolve_cost = (
                    f': {skill.evolves_to.sp} SP, '
                    f'{skill.evolve_medals} '
                    f'{em.get("Currency_Arena_Medal")}'
                    f'{evolve_secondary}'
                )
            else: evolve_cost = ''

            evolution = (
                f'**Evolves into:** '
                f'{skill.evolves_to.icon} {skill.evolves_to.name}'
                f'{evolve_cost}'
                if skill.evolves_to else None
            )

            refine_desc = '\n'.join(filter(None, [
                refined_skill_str,
                refine_header,
                refine_eff,
                generic_refines,
                evolution
            ]))
            embed.add_field(
                name = refined_title,
                value = refine_desc,
                inline = False
            )
        if (skill.type == SkillType.WEAPON
                or skill.type == SkillType.WEAPON_REFINED
                or (skill.type == SkillType.ASSIST and skill.is_staff)
        ):
            embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/skills/{skill.id}.png')
        else: embed.set_thumbnail(url=f'https://cdn.discordapp.com/emojis/{skill.icon.id}.png')

        return embed



    @staticmethod
    async def cmd_skill(params):
        tokens = params.split(',')
        if not tokens:
            return 'No input detected!', None, None
        skill = UnitLib.get_skill(tokens[0])
        if not skill:
            return f'Skill not found: {tokens[0]}.', None, None
        skill_embed = discord.Embed()
        zoom_state = False
        Command.format_skill(skill, skill_embed, zoom_state)
        return None, skill_embed, [skill, zoom_state]



    @staticmethod
    async def finalize_skill(bot_reply):
        await bot_reply.add_reaction('🔍')
        await bot_reply.add_reaction('⬆')
        await bot_reply.add_reaction('⬇')



    @staticmethod
    async def react_skill(reaction, bot_msg, embed, data):
        skill = data[0]
        if reaction.emoji == '🔍':
            data[1] = not data[1]
        elif reaction.emoji == '⬆':
            skill = skill.postreq[0] if len(skill.postreq) > 0 else skill
        elif reaction.emoji == '⬇':
            skill = skill.prereq1 if skill.prereq1 else skill
        elif reaction.emoji == '👁':
            embed.set_author(name=str(skill.id))
        else: return None, None, False
        data[0] = skill
        embed = Command.format_skill(skill, embed, data[1])
        return None, embed, True



    @staticmethod
    async def cmd_h_alias(params):
        tokens = params.split(',')
        names = [
            Command.filter_name(n)
            for n in tokens
        ]
        if len(names) != 2:
            return (
                'Wrong number of names found. '
                'Please enter two names, separated by a comma.',
                None, None
            )
        heroes = [UnitLib.get_hero(n) for n in names]
        if heroes[0] and not heroes[1]:
            UnitLib.insert_hero_alias(heroes[0], names[1])
            content = f'Added alias {names[1]} for {heroes[0].short_name}.'
            devs[0].send(
                f'{message.author.name}#{message.author.discriminator} '
                f'added alias {names[1]} for {heroes[0].short_name}.')
        elif heroes[1] and not heroes[0]:
            UnitLib.insert_hero_alias(heroes[1], names[0])
            content = f'Added alias {names[0]} for {heroes[1].short_name}.'
            devs[0].send(
                f'{message.author.name}#{message.author.discriminator} '
                f'added alias {names[0]} for {heroes[1].short_name}.')
        elif heroes[0] and heroes[1]:
            content = 'All names are already hero aliases!'
        else:
            content = 'Cannot find a valid hero name; need at least one.'
        return content, None, None



    @staticmethod
    async def finalize_h_alias(bot_reply):
        return



    @staticmethod
    async def react_h_alias(reaction, bot_msg, embed, data):
        return None, None, False



    @staticmethod
    async def cmd_s_alias(params):
        tokens = params.split(',')
        names = [
            Command.filter_name(n)
            for n in tokens
        ]
        if len(names) != 2:
            return (
                'Wrong number of names found. '
                'Please enter two names, separated by a comma.',
                None, None
            )
        skills = [UnitLib.get_skill(n) for n in names]
        if skills[0] and not skills[1]:
            UnitLib.insert_skill_alias(skills[0], names[1])
            content = f'Added alias {names[1]} for {skills[0].name}.'
            devs[0].send(
                f'{message.author.name}#{message.author.discriminator} '
                f'added alias {names[1]} for {skills[0].name}.')
        elif skills[1] and not skills[0]:
            UnitLib.insert_skill_alias(skills[1], names[0])
            content = f'Added alias {names[0]} for {skills[1].name}.'
            devs[0].send(
                f'{message.author.name}#{message.author.discriminator} '
                f'added alias {names[0]} for {skills[1].name}.')
        elif skills[0] and skills[1]:
            content = 'All names are already skill aliases!'
        else:
            content = 'Cannot find a valid skill name; need at least one.'
        return content, None, None



    @staticmethod
    async def finalize_s_alias(bot_reply):
        return



    @staticmethod
    async def react_s_alias(reaction, bot_msg, embed, data):
        return None, None, False

