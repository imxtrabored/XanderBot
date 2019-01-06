import discord
import asyncio
import re

from collections import Counter, namedtuple
from copy import copy
from enum import Enum
from functools import reduce
from operator import methodcaller
from string import punctuation, whitespace

from feh.emojilib import EmojiLib
from feh.hero import Hero, Color, UnitWeaponType, MoveType
from feh.hero import LegendElement, Stat, Rarity
from feh.skill import Skill, SkillType, SkillWeaponGroup
from feh.unitlib import UnitLib


transtab = str.maketrans('', '', punctuation + whitespace)
non_decimal = re.compile(r'[^\d]+')



BotReply = namedtuple('BotReply', 'bot_msg user_msg user feh_obj cmd_type embed data')



class CMDType(Enum):
    HERO = 1
    HERO_STATS = 2
    HERO_SKILLS = 3
    HERO_COMPARE = 4
    SKILL = 5
    SORT = 6



class XanderBotClient(discord.Client):


    def __init__(self, *, loop = None, **options):
        super().__init__(loop = loop, options = options)
        FILENAME = '../tokens.txt'
        file = open (FILENAME, 'r')
        self.token = file.readline().rstrip('\n')
        file.close()
        UnitLib.initialize()
        self.reactable_library = dict()
        self.editable_library = dict()



    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        EmojiLib.initialize(self)
        UnitLib.initialize_emojis(self)
        self.restrict_emojis = (
            str(EmojiLib.get(MoveType.INFANTRY      )),
            str(EmojiLib.get(MoveType.ARMOR         )),
            str(EmojiLib.get(MoveType.CAVALRY       )),
            str(EmojiLib.get(MoveType.FLIER         )),
            str(EmojiLib.get(UnitWeaponType.R_SWORD )),
            str(EmojiLib.get(UnitWeaponType.R_TOME  )),
            str(EmojiLib.get(UnitWeaponType.R_BOW   )),
            str(EmojiLib.get(UnitWeaponType.R_DAGGER)),
            str(EmojiLib.get(UnitWeaponType.R_BREATH)),
            str(EmojiLib.get(UnitWeaponType.B_LANCE )),
            str(EmojiLib.get(UnitWeaponType.B_TOME  )),
            str(EmojiLib.get(UnitWeaponType.B_BOW   )),
            str(EmojiLib.get(UnitWeaponType.B_DAGGER)),
            str(EmojiLib.get(UnitWeaponType.B_BREATH)),
            str(EmojiLib.get(UnitWeaponType.G_AXE   )),
            str(EmojiLib.get(UnitWeaponType.G_TOME  )),
            str(EmojiLib.get(UnitWeaponType.G_BOW   )),
            str(EmojiLib.get(UnitWeaponType.G_DAGGER)),
            str(EmojiLib.get(UnitWeaponType.G_BREATH)),
            str(EmojiLib.get(UnitWeaponType.C_BOW   )),
            str(EmojiLib.get(UnitWeaponType.C_DAGGER)),
            str(EmojiLib.get(UnitWeaponType.C_STAFF )),
            str(EmojiLib.get(UnitWeaponType.C_BREATH)),
        )


    async def forget_reactable(self, bot_msg):
        try:
            await asyncio.sleep(900)
        except asyncio.CancelledError:
            pass
        finally:
            print('deleted:')
            print(bot_msg)
            del self.reactable_library[bot_msg.id]



    def register_reactable(self, bot_msg, user_msg, user, feh_obj, cmd_type,
                           embed, data):
        self.reactable_library[bot_msg.id] = BotReply(
            bot_msg, user_msg, user, feh_obj, cmd_type, embed, data)
        print('registered:')
        print(bot_msg)
        return asyncio.create_task(self.forget_reactable(bot_msg))



    @staticmethod
    def filter_name(name):
        return name.lower().replace('+', 'plus').replace('-', 'minus').translate(transtab)



    @staticmethod
    def process_hero_mods(hero, args):
        bad_args = []
        rarity = hero.rarity
        merges = hero.merges
        boon = hero.boon
        bane = hero.bane
        level = hero.level
        futuremerges = False
        for token in args:
            token = XanderBotClient.filter_name(token[:24])
            print(token)
            # rarity, merges, iv, level, "summoned"
            # regex might be faster or slower here idk
            rarity_test = (token.replace('*', '').replace('star', '')
                           .replace('rarity', ''))
            if rarity_test.isdecimal():
                rarity = int(rarity_test)
            elif 'plusplus' in token or 'futuremerge' in token:
                merges = int(non_decimal.sub('', token))
                hero.newmerges = True
            elif 'merge' in token:
                merges = int(non_decimal.sub('', token))
                hero.newmerges = False
            elif 'plus' in token:
                # this might be merges, iv, or a skill
                plus_test = token.replace('plus', '')
                if plus_test.isdecimal():
                    merges = int(plus_test)
                    futuremerges = False
                elif (
                        token in [
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
                        token in (
                            'plusatk'   ,
                            'atkplus'   ,
                            'plusattack',
                            'attackplus',
                        )
                ):
                    boon = Stat.ATK
                elif (
                        token in (
                            'plusspd'  ,
                            'spdplus'  ,
                            'plusspeed',
                            'speedplus',
                        )
                ):
                    boon = Stat.SPD
                elif (
                        token in (
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
                        token in (
                            'plusres'       ,
                            'resplus'       ,
                            'plusresistance',
                            'resistanceplus',
                        )
                ):
                    boon = Stat.RES
                else:
                    skill = UnitLib.get_skill(token)
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
            elif 'boon' in token or 'asset' in token:
                if 'hp' in token or 'hitpoint' in token:
                    boon = Stat.HP
                elif 'atk' in token or 'attack' in token:
                    boon = Stat.ATK
                elif 'spd' in token or 'speed' in token:
                    boon = Stat.SPD
                elif 'def' in token or 'defense' in token or 'defence' in token:
                    boon = Stat.DEF
                elif 'res' in token or 'resistance' in token:
                    boon = Stat.RES
            elif 'minus' in token or 'bane' in token or 'flaw' in token:
                if 'hp' in token or 'hitpoint' in token:
                    bane = Stat.HP
                elif 'atk' in token or 'attack' in token:
                    bane = Stat.ATK
                elif 'spd' in token or 'speed' in token:
                    bane = Stat.SPD
                elif 'def' in token or 'defense' in token or 'defence' in token:
                    bane = Stat.DEF
                elif 'res' in token or 'resistance' in token:
                    bane = Stat.RES
            else:
                skill = UnitLib.get_skill(token)
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

        if (boon == Stat.NONE or bane == Stat.NONE) and boon != bane:
            boon = Stat.NONE
            bane = Stat.NONE
            bad_args.append(f'{hero.short_name} mismatched asset/flaw')
            # return some error
        print(boon)
        print(bane)
        hero.update_stat_mods(boon = boon, bane = bane, merges = merges,
                              rarity = rarity)
        return hero, bad_args



    async def cmd_hero(self, message, tokens):
        this_hero = self.unit_library.get_hero(tokens[0])
        hero_embed = discord.Embed(title = this_hero.name + ': ' + this_hero.epithet)
        description = ''
        description += this_hero.color.name + ' ' + this_hero.weapon_type.name + ' ' + this_hero.move_type.name + '\n'
        for i in range(this_hero.rarity):
            description += 'star'
        description += '\n'
        description += 'hp:' + str(this_hero.base_hp) + ' atk:' + str(this_hero.base_atk) + ' spd:' + str(this_hero.base_spd) + ' def:' + str(this_hero.base_def) + ' res:' + str(this_hero.base_res) + '\n'
        description += 'hp:' + str(this_hero.max_hp) + ' atk:' + str(this_hero.max_atk) + ' spd:' + str(this_hero.max_spd) + ' def:' + str(this_hero.max_def) + ' res:' + str(this_hero.max_res)
        hero_embed.description = description
        hero_embed.colour = discord.Colour.from_rgb(255, 0, 0)
        weapons = ''
        for skill in this_hero.skills.weapon:
            weapons += skill[0].name + ' ' + str(skill[1]) + ' star\n'
        if weapons == '': weapons = 'None'
        hero_embed.add_field(name='Weapons', value=weapons)
        assists = ''
        for skill in this_hero.skills.assist:
            assists += skill[0].name + ' ' + str(skill[1]) + ' star\n'
        if assists == '': assists = 'None'
        hero_embed.add_field(name='Assists', value=assists)
        specials = ''
        for specials in this_hero.skills.special:
            specials += skill[0].name + ' ' + str(skill[1]) + ' star\n'
        if specials == '': specials = 'None'
        hero_embed.add_field(name='Specials', value=specials)
        passives_a = ''
        for skill in this_hero.skills.passive_a:
            passives_a += skill[0].name + ' ' + str(skill[1]) + ' star\n'
        if passives_a == '': passives_a = 'None'
        hero_embed.add_field(name='Passive A', value=passives_a)
        passives_b = ''
        for skill in this_hero.skills.passive_b:
            passives_b += skill[0].name + ' ' + str(skill[1]) + ' star\n'
        if passives_b == '': passives_b = 'None'
        hero_embed.add_field(name='Passive B', value=passives_b)
        passives_c = ''
        for skill in this_hero.skills.passive_c:
            passives_c += skill[0].name + ' ' + str(skill[1]) + ' star\n'
        if passives_c == '': passives_c = 'None'
        hero_embed.add_field(name='Passive C', value=passives_c)
        await message.channel.send(embed=hero_embed)
        return



    def format_stats(self, hero, embed, zoom_state):
        if hero.is_legend:
            legend_info = (f'{EmojiLib.get(hero.legend_element)}'
                           f'{EmojiLib.get(hero.legend_boost)}'
                           )
        else: legend_info = ''
        title = (f'{hero.name}: {hero.epithet} '
                 f'{EmojiLib.get(hero.weapon_type)}'
                 f'{EmojiLib.get(hero.move_type)}'
                 f'{legend_info}'
                 )
        
        desc_rarity = str(EmojiLib.get(Rarity(hero.rarity))) * hero.rarity
        desc_level = f'{desc_rarity} LV. {hero.level}+{hero.merges}'
        desc_stat = ''
        if zoom_state:
            superboons = [
                '' if x == 0 else ' (+)' if x > 0 else ' (-)'
                for x in hero.get_boons_banes()
            ]
            lv1_stats = (
                f'{EmojiLib.get(Stat.HP)} HP: '
                f'{hero.lv1_hp}\n'
                f'{EmojiLib.get(Stat.ATK)} Attack: '
                f'{hero.lv1_atk}\n'
                f'{EmojiLib.get(Stat.SPD)} Speed: '
                f'{hero.lv1_spd}\n'
                f'{EmojiLib.get(Stat.DEF)} Defense: '
                f'{hero.lv1_def}\n'
                f'{EmojiLib.get(Stat.RES)} Resistance: '
                f'{hero.lv1_res}\n\n'
                f'Total: {hero.lv1_total}'
            )
            max_stats = (
                f'{EmojiLib.get(Stat.HP)} HP: '
                f'{hero.max_hp}{superboons[0]}\n'
                f'{EmojiLib.get(Stat.ATK)} Attack: '
                f'{hero.max_atk}{superboons[1]}\n'
                f'{EmojiLib.get(Stat.SPD)} Speed: '
                f'{hero.max_spd}{superboons[2]}\n'
                f'{EmojiLib.get(Stat.DEF)} Defense: '
                f'{hero.max_def}{superboons[3]}\n'
                f'{EmojiLib.get(Stat.RES)} Resistance: '
                f'{hero.max_res}{superboons[4]}\n\n'
                f'Total: {hero.max_total}'
            )
        else:
            stat_emojis = (
                f'{EmojiLib.get(Stat.HP )} · '
                f'{EmojiLib.get(Stat.ATK)} · '
                f'{EmojiLib.get(Stat.SPD)} · '
                f'{EmojiLib.get(Stat.DEF)} · '
                f'{EmojiLib.get(Stat.RES)} · '
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



    async def cmd_stats(self, message, tokens):
        zoom_state = False
        if not tokens:
            await message.channel.send('No input detected!')
            return
        this_hero = copy(UnitLib.get_hero(tokens[0]))
        if not this_hero:
            await message.channel.send(
                    f'Hero not found: {tokens[0]}. '
                    "Don't forget that modifiers should be delimited by commas.")
            return
        hero, bad_args = XanderBotClient.process_hero_mods(this_hero, tokens[1:])
        hero_embed = discord.Embed()
        hero_embed = self.format_stats(this_hero, hero_embed, zoom_state)
        
        hero_embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{this_hero.id}/Face.png')
        if bad_args:
            content = ('I did not understand the following arguments: '
                       f'{", ".join(bad_args)}')
        else:
            content = ''
        botreply = await message.channel.send(embed = hero_embed, content = content)
        self.register_reactable(botreply, message, message.author, this_hero,
                                CMDType.HERO_STATS, hero_embed, [zoom_state])
        await botreply.add_reaction('🔍')
        await botreply.add_reaction(EmojiLib.get(Rarity.ONE  ))
        await botreply.add_reaction(EmojiLib.get(Rarity.TWO  ))
        await botreply.add_reaction(EmojiLib.get(Rarity.THREE))
        await botreply.add_reaction(EmojiLib.get(Rarity.FOUR ))
        await botreply.add_reaction(EmojiLib.get(Rarity.FIVE ))
        await botreply.add_reaction('➕')
        await botreply.add_reaction('➖')
        await botreply.add_reaction('🔟')



    async def react_stats(self, reaction, bot_msg, user_msg, user, hero, cmd_type, embed, data):
        manage_msg = bot_msg.channel.permissions_for(bot_msg.author).manage_messages
        if   reaction.emoji == '🔍':
            data[0] = not data[0]
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == EmojiLib.get(Rarity.ONE  ):
            hero.update_stat_mods(rarity = 1)
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == EmojiLib.get(Rarity.TWO  ):
            hero.update_stat_mods(rarity = 2)
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == EmojiLib.get(Rarity.THREE):
            hero.update_stat_mods(rarity = 3)
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == EmojiLib.get(Rarity.FOUR ):
            hero.update_stat_mods(rarity = 4)
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == EmojiLib.get(Rarity.FIVE ):
            hero.update_stat_mods(rarity = 5)
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == '➕':
            hero.update_stat_mods(merges = hero.merges + 1)
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == '➖':
            hero.update_stat_mods(merges = hero.merges - 1)
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == '🔟':
            hero.update_stat_mods(merges = 10)
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == '⏩':
            hero.newmerges = True
            hero.update_stat_mods(merges = hero.merges)
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
            asyncio.create_task(bot_msg.add_reaction('⏪'))
            asyncio.create_task(bot_msg.add_reaction('⏩'))
        elif reaction.emoji == '⏪':
            hero.newmerges = False
            hero.update_stat_mods(merges = hero.merges)
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
            asyncio.create_task(bot_msg.add_reaction('⏪'))
            asyncio.create_task(bot_msg.add_reaction('⏩'))
        elif reaction.emoji == '💾':
            embed.set_footer(text = 'Coming Soon!',
                             icon_url = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/146/floppy-disk_1f4be.png')
        elif reaction.emoji == '👁':
            embed.set_author(name=str(hero.id))
        else: return
        embed = self.format_stats(hero, embed, data[0])
        await bot_msg.edit(embed = embed)



    def format_hero_skills(self, hero, embed, zoom_state):
        if hero.is_legend:
            legend_info = (f'{EmojiLib.get(hero.legend_element)}'
                           f'{EmojiLib.get(hero.legend_boost)}'
                           )
        else: legend_info = ''

        title = (
            f'{hero.name}: {hero.epithet} '
            f'{EmojiLib.get(hero.weapon_type)}'
            f'{EmojiLib.get(hero.move_type)}'
            f'{legend_info}'
        )

        desc_rarity = (str(EmojiLib.get(Rarity(hero.rarity))) * hero.rarity
                       if not zoom_state else '-')
        desc_skills = ''
        if zoom_state:
            weapon    = ([f'{EmojiLib.get(Rarity(skill[1]))} · '
                          f'{skill[0].icon} '
                          f'{skill[0].name}'
                          for skill in hero.weapon   ]
                          if hero.weapon    else ('None',))
            assist    = ([f'{EmojiLib.get(Rarity(skill[1]))} · '
                          f'{skill[0].icon} '
                          f'{skill[0].name}'
                          for skill in hero.assist   ]
                          if hero.assist    else ('None',))
            special   = ([f'{EmojiLib.get(Rarity(skill[1]))} · '
                          f'{skill[0].icon} '
                          f'{skill[0].name}'
                          for skill in hero.special  ]
                          if hero.special   else ('None',))
            passive_a = ([f'{EmojiLib.get(Rarity(skill[1]))} · '
                          f'{skill[0].icon} '
                          f'{skill[0].name}'
                          for skill in hero.passive_a]
                          if hero.passive_a else ('None',))
            passive_b = ([f'{EmojiLib.get(Rarity(skill[1]))} · '
                          f'{skill[0].icon} '
                          f'{skill[0].name}'
                          for skill in hero.passive_b]
                          if hero.passive_b else ('None',))
            passive_c = ([f'{EmojiLib.get(Rarity(skill[1]))} · '
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
                f'{EmojiLib.get(SkillType.WEAPON )}{weapon .name}\n'
                f'{EmojiLib.get(SkillType.ASSIST )}{assist .name}\n'
                f'{EmojiLib.get(SkillType.SPECIAL)}{special.name}\n\n'
                f'{passive_a.icon}'
                f'{passive_a.skill_rank if passive_a.skill_rank > 0 else ""} · '
                f'{passive_b.icon}'
                f'{passive_b.skill_rank if passive_b.skill_rank > 0 else ""} · '
                f'{passive_c.icon}'
                f'{passive_c.skill_rank if passive_c.skill_rank > 0 else ""}'
            )

        embed.clear_fields()
        description = f'{desc_rarity}\n\n{desc_skills}'
        embed.add_field(name = title, value = description, inline=False)
        
        if zoom_state:
            print(weapon)
            embed.add_field(name = f'{EmojiLib.get(SkillType.WEAPON   )} '
                                    'Weapon' ,
                            value = '\n'.join(weapon   ), inline = True )
            embed.add_field(name = f'{EmojiLib.get(SkillType.ASSIST   )} '
                                    'Assist' ,
                            value = '\n'.join(assist   ), inline = True )
            embed.add_field(name = f'{EmojiLib.get(SkillType.SPECIAL  )} '
                                    'Special',
                            value = '\n'.join(special  ), inline = False)
            embed.add_field(name = f'{EmojiLib.get(SkillType.PASSIVE_A)} '
                                    'Passive',
                            value = '\n'.join(passive_a), inline = True )
            embed.add_field(name = f'{EmojiLib.get(SkillType.PASSIVE_B)} '
                                    'Passive',
                            value = '\n'.join(passive_b), inline = True )
            embed.add_field(name = f'{EmojiLib.get(SkillType.PASSIVE_C)} '
                                    'Passive',
                            value = '\n'.join(passive_c), inline = False)
        return embed
        return



    async def cmd_hero_skills(self, message, tokens):
        if not tokens:
            await message.channel.send('No input detected!')
            return
        zoom_state = False
        this_hero = copy(UnitLib.get_hero(tokens[0]))
        if not this_hero:
            await message.channel.send(
                f'Hero not found: {tokens[0]}. '
                 "Don't forget that modifiers should be delimited by commas.")
            return
        XanderBotClient.process_hero_mods(this_hero, tokens[1:])
        hero_embed = discord.Embed()
        hero_embed = self.format_hero_skills(this_hero, hero_embed, zoom_state)
        
        hero_embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{this_hero.id}/Face.png')

        botreply = await message.channel.send(embed=hero_embed)
        self.register_reactable(botreply, message, message.author, this_hero,
                                CMDType.HERO_SKILLS, hero_embed, [zoom_state])
        await botreply.add_reaction('🔍')
        await botreply.add_reaction(EmojiLib.get(Rarity.ONE  ))
        await botreply.add_reaction(EmojiLib.get(Rarity.TWO  ))
        await botreply.add_reaction(EmojiLib.get(Rarity.THREE))
        await botreply.add_reaction(EmojiLib.get(Rarity.FOUR ))
        await botreply.add_reaction(EmojiLib.get(Rarity.FIVE ))



    async def react_hero_skills(self, reaction, bot_msg, user_msg, user, hero,
                                cmd_type, embed, data):
        manage_msg = bot_msg.channel.permissions_for(bot_msg.author).manage_messages
        if   reaction.emoji == '🔍':
            data[0] = not data[0]
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == EmojiLib.get(Rarity.ONE  ):
            hero.update_stat_mods(rarity = 1)
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == EmojiLib.get(Rarity.TWO  ):
            hero.update_stat_mods(rarity = 2)
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == EmojiLib.get(Rarity.THREE):
            hero.update_stat_mods(rarity = 3)
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == EmojiLib.get(Rarity.FOUR ):
            hero.update_stat_mods(rarity = 4)
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == EmojiLib.get(Rarity.FIVE ):
            hero.update_stat_mods(rarity = 5)
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == '💾':
            embed.set_footer(text = 'Coming Soon!',
                             icon_url = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/146/floppy-disk_1f4be.png')
        elif reaction.emoji == '👁':
            embed.set_author(name=str(hero.id))
        else: return
        embed = self.format_hero_skills(hero, embed, data[0])
        await bot_msg.edit(embed = embed)



    def format_compare(self, heroes, embed, zoom_state):
        embed.clear_fields()
        print(len(heroes))
        if len(heroes) < 1:
            embed.description = 'No heroes found.'
            return embed
        elif len(heroes) == 1:
            embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{heroes[0].id}/Face.png')
            return self.format_stats(heroes[0], embed, zoom_state)
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
                    f'{hero.rarity}{EmojiLib.get(Rarity(hero.rarity))} '
                    f'LV. {hero.level}+{hero.merges}\n'
                    f'{EmojiLib.get(Stat.HP)} HP: '
                    f'{hero.max_hp}{superboons[0]}\n'
                    f'{EmojiLib.get(Stat.ATK)} Attack: '
                    f'{hero.max_atk}{superboons[1]}\n'
                    f'{EmojiLib.get(Stat.SPD)} Speed: '
                    f'{hero.max_spd}{superboons[2]}\n'
                    f'{EmojiLib.get(Stat.DEF)} Defense: '
                    f'{hero.max_def}{superboons[3]}\n'
                    f'{EmojiLib.get(Stat.RES)} Resistance: '
                    f'{hero.max_res}{superboons[4]}\n\n'
                    f'BST: {hero.max_total}'
            )

            embed.add_field(
                    name = (
                        f'{hero.short_name} '
                        f'{EmojiLib.get(hero.weapon_type)} '
                        f'{EmojiLib.get(hero.move_type)} '
                    ),
                    value = max_stats,
                    inline = True
            )

        if len(heroes) == 2:
            stat_sort  = sorted(heroes,
                                key = lambda h: h.max_hp,
                                reverse = True)
            if stat_sort[0].max_hp > stat_sort[-1].max_hp:
                hp_str = (
                    f'{EmojiLib.get(Stat.HP)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_hp - stat_sort[1].max_hp} '
                    'more HP.'
                )
            else: hp_str = f'{EmojiLib.get(Stat.HP)} Equal HP'

            stat_sort  = sorted(heroes,
                                key = lambda h: h.max_atk,
                                reverse = True)
            if stat_sort[0].max_atk > stat_sort[-1].max_atk:
                atk_str = (
                    f'{EmojiLib.get(Stat.ATK)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_atk - stat_sort[1].max_atk} '
                    'more Attack.'
                )
            else: atk_str = f'{EmojiLib.get(Stat.ATK)} Equal Attack.'

            stat_sort  = sorted(heroes,
                                key = lambda h: h.max_spd,
                                reverse = True)
            if stat_sort[0].max_spd > stat_sort[-1].max_spd:
                spd_str = (
                    f'{EmojiLib.get(Stat.SPD)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_spd - stat_sort[1].max_spd} '
                    'more Speed.'
                )
            else: spd_str = f'{EmojiLib.get(Stat.SPD)} Equal Speed.'

            stat_sort  = sorted(heroes,
                                key = lambda h: h.max_def,
                                reverse = True)
            if stat_sort[0].max_def > stat_sort[-1].max_def:
                def_str = (
                    f'{EmojiLib.get(Stat.DEF)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_def - stat_sort[1].max_def} '
                    'more Defense.'
                )
            else: def_str = f'{EmojiLib.get(Stat.DEF)} Equal Defense.'

            stat_sort  = sorted(heroes,
                                key = lambda h: h.max_res,
                                reverse = True)
            if stat_sort[0].max_res > stat_sort[-1].max_res:
                res_str = (
                    f'{EmojiLib.get(Stat.RES)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_res - stat_sort[1].max_res} '
                    'more Resistance.'
                )
            else: res_str = f'{EmojiLib.get(Stat.RES)} Equal Resistance.'

            stat_sort  = sorted(heroes,
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
            stat_sort  = sorted(heroes,
                                key = lambda h: h.max_hp,
                                reverse = True)
            if stat_sort[0].max_hp > stat_sort[-1].max_hp:
                max_list = ", ".join([
                        h.short_name for h in heroes
                        if h.max_hp == stat_sort[0].max_hp])
                hp_str = (
                    f'{EmojiLib.get(Stat.HP)} '
                    f'Greatest HP: {stat_sort[0].max_hp} '
                    f'({max_list})'
                )
            else: hp_str = (f'{EmojiLib.get(Stat.HP)} '
                            'All heroes have equal HP.')

            stat_sort  = sorted(heroes,
                                key = lambda h: h.max_atk,
                                reverse = True)
            if stat_sort[0].max_atk > stat_sort[-1].max_atk:
                max_list = ", ".join([
                        h.short_name for h in heroes
                        if h.max_atk == stat_sort[0].max_atk])
                atk_str = (
                    f'{EmojiLib.get(Stat.ATK)} '
                    f'Greatest Attack: {stat_sort[0].max_atk} '
                    f'({max_list})'
                )
            else: atk_str = (f'{EmojiLib.get(Stat.ATK)} '
                             'All heroes have equal Attack.')

            stat_sort  = sorted(heroes,
                                key = lambda h: h.max_spd,
                                reverse = True)
            if stat_sort[0].max_spd > stat_sort[-1].max_spd:
                max_list = ", ".join([
                        h.short_name for h in heroes
                        if h.max_spd == stat_sort[0].max_spd])
                spd_str = (
                    f'{EmojiLib.get(Stat.SPD)} '
                    f'Greatest Speed: {stat_sort[0].max_spd} '
                    f'({max_list})'
                )
            else: spd_str = (f'{EmojiLib.get(Stat.SPD)} '
                             'All heroes have equal Speed.')

            stat_sort  = sorted(heroes,
                                key = lambda h: h.max_def,
                                reverse = True)
            if stat_sort[0].max_def > stat_sort[-1].max_def:
                max_list = ", ".join([
                        h.short_name for h in heroes
                        if h.max_def == stat_sort[0].max_def])
                def_str = (
                    f'{EmojiLib.get(Stat.DEF)} '
                    f'Greatest Defense: {stat_sort[0].max_def} '
                    f'({max_list})'
                )
            else: def_str = (f'{EmojiLib.get(Stat.DEF)} '
                             'All heroes have equal Defense.')

            stat_sort  = sorted(heroes,
                                key = lambda h: h.max_res,
                                reverse = True)
            if stat_sort[0].max_res > stat_sort[-1].max_res:
                max_list = ", ".join([
                        h.short_name for h in heroes
                        if h.max_res == stat_sort[0].max_res])
                res_str = (
                    f'{EmojiLib.get(Stat.RES)} '
                    f'Greatest Resistance: {stat_sort[0].max_res} '
                    f'({max_list})'
                )
            else: res_str = (f'{EmojiLib.get(Stat.RES)} '
                             'All heroes have equal Resistance.')

            stat_sort  = sorted(heroes,
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



    async def cmd_compare(self, message, tokens):
        if len(tokens) < 2:
            await message.channel.send('No input detected!')
            return
        tokens = tokens[1]
        zoom_state = False
        hero_embed = discord.Embed()
        print(tokens)
        bad_args = []
        if ';' not in tokens:
            # slow mode
            tokens = tokens.split(',')
            heroes = []
            for param in tokens:
                this_hero = UnitLib.get_hero(param)
                if this_hero: heroes.append(this_hero)
                else:
                    if len(heroes) == 0:
                        bad_args.append(param)
                    else:
                        heroes[-1], bad_arg = self.process_hero_mods(heroes[-1], [param])
                        bad_args.extend(bad_arg)

            hero_embed.set_author(
                    name = ('Please delimit compared heroes with semicolons (;)'
                            'in the future to improve speed and clarity.')
            )
            # hero_embed = self.format_stats(this_hero, hero_embed, zoom_state)
        else:
            # normal mode
            hero_list = map(methodcaller('split', ','), tokens.split(';'))
            heroes = []
            for param in hero_list:
                this_hero = UnitLib.get_hero(param[0])
                if this_hero:
                    this_hero, bad_arg = self.process_hero_mods(this_hero, param[1:])
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
        hero_embed = self.format_compare(heroes, hero_embed, zoom_state)

        if bad_args:
            content = ( 'I did not understand the following arguments: '
                       f'{", ".join(bad_args)}')
        else:
            content = ''
        botreply = await message.channel.send(content = content, embed = hero_embed)
        self.register_reactable(botreply, message, message.author, 'this_hero',
                                CMDType.HERO_COMPARE, hero_embed, [zoom_state])



    async def react_compare(self, reaction, bot_msg, user_msg, user, hero,
                            cmd_type, embed, data):
        pass



    def format_skill(self, skill, embed, zoom_state):
        type_icon = (EmojiLib.get(skill.weapon_type)
                     if skill.weapon_type else EmojiLib.get(skill.type))
        seal_icon = (EmojiLib.get(SkillType.PASSIVE_SEAL)
                     if skill.type != SkillType.PASSIVE_SEAL and skill.is_seal
                     else "")
        title = f'{skill.icon} {skill.name} · {type_icon}{seal_icon}'

        if (skill.type == SkillType.WEAPON
            or skill.type == SkillType.WEAPON_REFINED
            ):
            if any([
                skill.eff_infantry,
                skill.eff_armor   ,
                skill.eff_cavalry ,
                skill.eff_flier   ,
                skill.eff_magic   ,
                skill.eff_dragon  ,
            ]):
                eff_list = [' Eff: ']
                if skill.eff_infantry: eff_list.append(str(EmojiLib.get(MoveType.INFANTRY)))
                if skill.eff_armor   : eff_list.append(str(EmojiLib.get(MoveType.ARMOR   )))
                if skill.eff_cavalry : eff_list.append(str(EmojiLib.get(MoveType.CAVALRY )))
                if skill.eff_flier   : eff_list.append(str(EmojiLib.get(MoveType.FLIER   )))
                if skill.eff_magic   :
                    eff_list.append(str(EmojiLib.get(SkillWeaponGroup.R_TOME)))
                    eff_list.append(str(EmojiLib.get(SkillWeaponGroup.B_TOME)))
                    eff_list.append(str(EmojiLib.get(SkillWeaponGroup.G_TOME)))
                if skill.eff_dragon  : eff_list.append(str(EmojiLib.get(SkillWeaponGroup.S_BREATH)))
                effective = ''.join(eff_list)
            else: effective = ''

            weapon_desc = (f'Mt: {skill.disp_atk} Rng: {skill.range}{effective}')
        elif skill.type == SkillType.SPECIAL:
            weapon_desc = f'{EmojiLib.get(SkillType.SPECIAL)} {skill.special_cd}'
        else: weapon_desc = None

        prereq = (
            '_This skill can only be equipped by its original unit._'
            if skill.exclusive else
            f'**Requires:** {skill.prereq1.icon} {skill.prereq1.name}'
            f'or {skill.prereq2.icon} {skill.prereq2.name}'
            if skill.prereq2
            else
            f'**Requires:** {skill.prereq1.icon} {skill.prereq1.name}'
            if skill.prereq1
            else None
        )

        restrictions = None
        if skill.type != SkillType.WEAPON:
            if skill.is_staff:
                restrictions = "_This skill can only be equipped by staff users._"
            else:
                restrictions = (
                    skill.infantry,
                    skill.armor   ,
                    skill.cavalry ,
                    skill.flier   ,
                    skill.r_sword ,
                    skill.r_tome  ,
                    skill.r_dagger,
                    skill.r_bow   ,
                    skill.r_breath,
                    skill.b_lance ,
                    skill.b_bow   ,
                    skill.b_dagger,
                    skill.b_tome  ,
                    skill.b_breath,
                    skill.g_axe   ,
                    skill.g_bow   ,
                    skill.g_dagger,
                    skill.g_tome  ,
                    skill.g_breath,
                    skill.c_bow   ,
                    skill.c_dagger,
                    skill.c_staff ,
                    skill.c_breath,
                )
                restrict_list = [self.restrict_emojis[count]
                                 for count, value in enumerate(restrictions)
                                 if not value]
                if restrict_list:
                    restrictions = f'**Cannot use:** {"".join(restrict_list)}'

        sp = f'**SP:** {skill.sp}'

        if (skill.type == SkillType.WEAPON and not skill.exclusive
            and ((skill.tier <= 2 and not skill.is_staff) or skill.tier <= 1)):
            learnable = 'Basic weapon available to most eligible heroes.'
        elif (skill.type == SkillType.ASSIST and skill.is_staff
              and skill.tier <= 1):
            learnable = 'Basic assist available to all staff users.'
        # elif reduce(lambda x, y: x + len(y), skill.learnable[1:], 0) > 20:
        elif (
                len(skill.learnable[1]) + len(skill.learnable[2])
                + len(skill.learnable[3]) + len(skill.learnable[4])
                + len(skill.learnable[5]) > 20
        ):
            learnable = 'Over 20 heroes know this skill.'
        else:
            learnable = '\n'.join(filter(None, [
                f'{EmojiLib.get(Rarity(count))}: '
                f'{", ".join((hero.short_name for hero in hero_list))}'
                if hero_list else None
                for count, hero_list in enumerate(skill.learnable[1:], 1)
            ]))

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

            description = '\n'.join(filter(None, [
                weapon_desc,
                skill.description,
                prereq,
                restrictions,
                sp,
                cumul_sp,
                '**Available from:**',
                learnable,
                postreqs
            ]))
        else:
            description = '\n'.join(filter(None, [
                weapon_desc,
                skill.description,
                prereq,
                restrictions,
                sp,
                '**Available from:**',
                learnable
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
                    f'{EmojiLib.get("Currency_Refining_Stone")}'
                    if skill.refine_stones else
                    f', {skill.refine_dew} '
                    f'{EmojiLib.get("Currency_Divine_Dew")}'
                    if skill.refine_dew else ''
                )
                refine_cost = (
                    f' {skill.refine_sp} SP, '
                    f'{skill.refine_medals} '
                    f'{EmojiLib.get("Currency_Arena_Medal")}'
                    f'{refine_secondary}'
                )
            else: refine_cost = ''

            refine_header = (f'**Refine options:**{refine_cost}'
                             if skill.refinable else None)
            if skill.refined_version:
                refined_skill = skill.refined_version
                ref_type_icon = (EmojiLib.get(skill.weapon_type)
                                 if skill.weapon_type
                                 else EmojiLib.get(skill.type))
                refined_title = (f'Weapon Refinery\n{refined_skill.icon} '
                                 f'Refined {skill.name} · {type_icon}'
                                 )
                if any([
                    refined_skill.eff_infantry,
                    refined_skill.eff_armor,
                    refined_skill.eff_cavalry,
                    refined_skill.eff_flier,
                    refined_skill.eff_magic,
                    refined_skill.eff_dragon
                ]):
                    eff_list = [' Eff: ']
                    if refined_skill.eff_infantry: eff_list.append(str(EmojiLib.get(MoveType.INFANTRY)))
                    if refined_skill.eff_armor   : eff_list.append(str(EmojiLib.get(MoveType.ARMOR   )))
                    if refined_skill.eff_cavalry : eff_list.append(str(EmojiLib.get(MoveType.CAVALRY )))
                    if refined_skill.eff_flier   : eff_list.append(str(EmojiLib.get(MoveType.FLIER   )))
                    if refined_skill.eff_magic   :
                        eff_list.append(str(EmojiLib.get(SkillWeaponGroup.R_TOME)))
                        eff_list.append(str(EmojiLib.get(SkillWeaponGroup.B_TOME)))
                        eff_list.append(str(EmojiLib.get(SkillWeaponGroup.G_TOME)))
                    if refined_skill.eff_dragon  : eff_list.append(str(EmojiLib.get(SkillWeaponGroup.S_BREATH)))
                    effective = ''.join(eff_list)
                else: effective = ''
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

            if zoom_state:
                generic_refines = '\n'.join([
                    f'{refine.icon}: {refine.description}'
                    for refine in [
                        skill.refine_staff1,
                        skill.refine_staff2,
                        skill.refine_atk,
                        skill.refine_spd,
                        skill.refine_def,
                        skill.refine_res
                    ]
                    if refine
                ])
            else:
                generic_refines = ', '.join([
                    str(refine.icon)
                    for refine in [
                        skill.refine_staff1,
                        skill.refine_staff2,
                        skill.refine_atk,
                        skill.refine_spd,
                        skill.refine_def,
                        skill.refine_res
                    ]
                    if refine
                ])

            if zoom_state and skill.evolves_to:
                evolve_secondary = (
                    f', {skill.evolve_stones} '
                    f'{EmojiLib.get("Currency_Refining_Stone")}'
                    if skill.evolve_stones else
                    f', {skill.evolve_dew} '
                    f'{EmojiLib.get("Currency_Divine_Dew")}'
                    if skill.evolve_dew else ''
                )
                evolve_cost = (
                    f': {skill.evolves_to.sp} SP, '
                    f'{skill.evolve_medals} '
                    f'{EmojiLib.get("Currency_Arena_Medal")}'
                    f'{evolve_secondary}'
                )
            else: evolve_cost = ''

            evolution = (f'**Evolves into:** '
                         f'{skill.evolves_to.icon} {skill.evolves_to.name}'
                         f'{evolve_cost}'
                         if skill.evolves_to else None)

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



    async def cmd_skill(self, message, tokens):
        if not tokens:
            await message.channel.send('No input detected!')
            return
        this_skill = UnitLib.get_skill(tokens[0])
        if not this_skill:
            await message.channel.send(f'Skill not found: {tokens[0]}.')
            return
        skill_embed = discord.Embed()
        zoom_state = False
        self.format_skill(this_skill, skill_embed, zoom_state)
        botreply = await message.channel.send(embed = skill_embed)
        self.register_reactable(botreply, message, message.author, [this_skill], CMDType.SKILL, skill_embed, [zoom_state])
        await botreply.add_reaction('🔍')
        await botreply.add_reaction('⬆')
        await botreply.add_reaction('⬇')



    async def react_skill(self, reaction, bot_msg, user_msg, user, skill, cmd_type, embed, data):
        manage_msg = bot_msg.channel.permissions_for(bot_msg.author).manage_messages

        if reaction.emoji == '🔍':
            data[0] = not data[0]
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == '⬆':
            skill[0] = skill[0].postreq[0] if len(skill[0].postreq) > 0 else skill[0]
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == '⬇':
            skill[0] = skill[0].prereq1 if skill[0].prereq1 else skill[0]
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        elif reaction.emoji == '👁':
            embed.set_author(name=str(skill[0].id))
            if manage_msg: asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        else: return
        embed = self.format_skill(skill[0], embed, data[0])
        await bot_msg.edit(embed = embed)



    async def add_hero_alias(message, tokens):
        names = [
            self.filter_name(n)
            for n in tokens
        ]
        if len(names) != 2:
            await message.channel.send(
                'Wrong number of names found. '
                'Please enter two names, separated by a comma.'
            )
        heroes = [UnitLib.get_hero(n) for n in names]
        if heroes[0] and not heroes[1]:
            UnitLib.insert_hero_alias(heroes[0], names[1])
            await message.channel.send(
                f'Added alias {names[1]} for {heroes[0].short_name}.')
            client.get_user(151913154803269633).send(
                f'{message.author.name}#{message.author.discriminator} '
                f'added alias {names[1]} for {heroes[0].short_name}.')
        elif heroes[1] and not heroes[0]:
            UnitLib.insert_hero_alias(heroes[1], names[0])
            await message.channel.send(
                f'Added alias {names[0]} for {heroes[1].short_name}.')
            client.get_user(151913154803269633).send(
                f'{message.author.name}#{message.author.discriminator} '
                f'added alias {names[0]} for {heroes[1].short_name}.')
        elif heroes[0] and heroes[1]:
            await message.channel.send('All names are already hero aliases!')
        else:
            await message.channel.send('Cannot find a valid hero name; need at least one.')



    async def add_skill_alias(message, tokens):
        names = [
            XanderBotClient.filter_name(n)
            for n in lower_message.split(' ', 1)[1].split(',')
        ]
        if len(names) != 2:
            await message.channel.send(
                'Wrong number of names found. '
                'Please enter two names, separated by a comma.'
            )
        skills = [UnitLib.get_skill(n) for n in names]
        if skills[0] and not skills[1]:
            UnitLib.insert_skill_alias(skills[0], names[1])
            await message.channel.send(
                f'Added alias {names[1]} for {skills[0].name}.')
            client.get_user(151913154803269633).send(
                f'{message.author.name}#{message.author.discriminator} '
                f'added alias {names[1]} for {skills[0].name}.')
        elif skills[1] and not skills[0]:
            UnitLib.insert_skill_alias(skills[1], names[0])
            await message.channel.send(
                f'Added alias {names[0]} for {skills[1].name}.')
            client.get_user(151913154803269633).send(
                f'{message.author.name}#{message.author.discriminator} '
                f'added alias {names[0]} for {skills[1].name}.')
        elif skills[0] and skills[1]:
            await message.channel.send('All names are already skill aliases!')
        else:
            await message.channel.send('Cannot find a valid skill name; need at least one.')



    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        test_string = message.content[:4].lower()
        if not (test_string.startswith('f?') or test_string.startswith('feh?')):
            return

        lower_message = message.content.lower()

        if lower_message.startswith('f?'):
            lower_message = lower_message[2:]
        elif lower_message.startswith('feh?'):
            lower_message = lower_message[4:]
        split_command = lower_message.split(' ', 1)
        if len(split_command) > 1:
            tokens = split_command[1].split(',')
        else: tokens = []
        try:
            #TODO: kind of gross line, also investigate if RE or map is faster here?

            if   lower_message.startswith('hero') or lower_message.startswith('unit'):
                await self.cmd_hero(message, tokens)
            elif lower_message.startswith('stat'):
                await self.cmd_stats(message, tokens)
            elif lower_message.startswith('skills'):
                await self.cmd_hero_skills(message, tokens)
            elif lower_message.startswith('compare'):
                await self.cmd_compare(message, split_command)
            elif lower_message.startswith('skill '):
                await self.cmd_skill(message, tokens)


            #debug commands

            if (lower_message.startswith('emojis')
                and (message.author.id == 151913154803269633
                     or message.author.id == 196379129472352256)):
                emojilisttemp = sorted(self.emojis, key=lambda q: (q.name))
                for e in emojilisttemp:
                    print(e.name)
                    await message.channel.send(str(e) + str(e.id))

            elif (lower_message.startswith('reload')
                  and (message.author.id == 151913154803269633
                       or message.author.id == 196379129472352256)):
                reply = await message.channel.send(
                    'Rebuilding hero, skill, and emoji indices...')
                UnitLib.initialize()
                UnitLib.initialize_emojis(self)
                EmojiLib.initialize(self)
                await reply.edit(content = 'Done rebuilding all indices.')

            elif (lower_message.startswith('say')
                  and (message.author.id == 151913154803269633
                       or message.author.id == 196379129472352256)):
                payload = message.content.split(' ', 2)[1:]
                await self.get_channel(int(payload[0])).send(payload[1])

            elif lower_message.startswith('addalias'):
                await self.add_hero_alias(message, tokens)

            elif lower_message.startswith('skillalias'):
                await self.add_skill_alias(message, tokens)

            elif lower_message.startswith('whoami'):
                await message.channel.send(f"You're <{message.author.id}>!")

            elif lower_message.startswith('test'):
                counter = 0
                tmp = await message.channel.send('Calculating messages...')
                async for msg in message.channel.history(limit=100):
                    if msg.author == message.author:
                        counter += 1

                await tmp.edit(content='You have {} messages.'.format(counter))
            elif message.content.startswith('sleep'):
                with message.channel.typing():
                    await asyncio.sleep(5.0)
                    await message.channel.send('Done sleeping.')
        except:
            await message.channel.send("An unknown error has occured.")
            raise



    async def on_reaction_add(self, reaction, user):
        if (reaction.message.author != client.user
            or user == client.user
            or reaction.message.id not in self.reactable_library): return
        msg_bundle = self.reactable_library[reaction.message.id]
        if user != msg_bundle.user: return
        if(msg_bundle.cmd_type == CMDType.HERO_STATS):
            await self.react_stats(reaction, *msg_bundle)
        elif(msg_bundle.cmd_type == CMDType.HERO_SKILLS):
            await self.react_hero_skills(reaction, *msg_bundle)
        elif(msg_bundle.cmd_type == CMDType.SKILL):
            await self.react_skill(reaction, *msg_bundle)



client = XanderBotClient()
client.run(client.token)
