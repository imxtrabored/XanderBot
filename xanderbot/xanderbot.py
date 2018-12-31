import discord
import asyncio

from copy import copy
from collections import namedtuple
from enum import Enum
from functools import reduce

from feh.emojilib import EmojiLib
from feh.hero import Hero, Color, UnitWeaponType, MoveType
from feh.hero import LegendElement, Stat, Rarity
from feh.skill import Skill, SkillType, SkillWeaponGroup
from feh.unitlib import UnitLib



BotReply = namedtuple('BotReply', 'bot_msg user_msg user feh_obj cmd_type embed data')



class CMDType(Enum):
    HERO = 1
    HERO_STATS = 2
    HERO_SKILLS = 3
    SKILL = 4
    SORT = 5



class XanderBotClient(discord.Client):


    def __init__(self, *, loop=None, **options):
        super().__init__(loop = loop, options = options)
        FILENAME = '../tokens.txt'
        file = open (FILENAME, 'r')
        self.token = file.readline().rstrip('\n')
        file.close()
        print('loading data...')
        self.unit_library = UnitLib.initialize()
        print('done.')
        self.reactable_library = dict()
        self.editable_library = dict()



    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        self.emojilib = EmojiLib.initialize(self)
        UnitLib.initialize_emojis(self)



    async def forget_reactable(self, bot_msg):
        try:
            await asyncio.sleep(600)
        except asyncio.CancelledError:
            pass
        finally:
            print('deleted:')
            print(bot_msg)
            del self.reactable_library[bot_msg.id]



    def register_reactable(
        self, bot_msg, user_msg, user, feh_obj, cmd_type, embed, data):
        self.reactable_library[bot_msg.id] = BotReply(
            bot_msg, user_msg, user, feh_obj, cmd_type, embed, data)
        print('registered:')
        print(bot_msg)
        return asyncio.create_task(self.forget_reactable(bot_msg))



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
        title = (f'{hero.name}: {hero.epithet} '
                 f'{EmojiLib.get(hero.weapon_type)}'
                 f'{EmojiLib.get(hero.move_type)}'
                 )
        
        desc_rarity = str(EmojiLib.get(Rarity(hero.rarity))) * hero.rarity
        desc_level = f'{desc_rarity} LV. {hero.level}+{hero.merges}'
        desc_stat = ''
        if zoom_state:
            lv1_stats = 'HP: ' + str(hero.lv1_hp)
            lv1_stats += '\nAttack: ' + str(hero.lv1_atk)
            lv1_stats += '\nSpeed: ' + str(hero.lv1_spd)
            lv1_stats += '\nDefense: ' + str(hero.lv1_def)
            lv1_stats += '\nResistance: ' + str(hero.lv1_res)
            max_stats = 'HP: '     + str(hero.max_hp)
            max_stats += '\nAttack: ' + str(hero.max_atk)
            max_stats += '\nSpeed: ' + str(hero.max_spd)
            max_stats += '\nDefense: ' + str(hero.max_def)
            max_stats += '\nResistance: ' + str(hero.max_res)
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
        this_hero = copy(UnitLib.get_hero(tokens[0]))
        hero_embed = discord.Embed()
        hero_embed = self.format_stats(this_hero, hero_embed, zoom_state)
        
        hero_embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{this_hero.id}/Face.png')

        botreply = await message.channel.send(embed=hero_embed)
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



    async def react_stats(self, reaction, bot_msg, user_msg, user, hero, cmd_type, embed, data):
        if   reaction.emoji == '🔍':
            data[0] = not data[0]
        elif reaction.emoji == EmojiLib.get(Rarity.ONE  ):
            hero.update_stat_mods(rarity = 1)
        elif reaction.emoji == EmojiLib.get(Rarity.TWO  ):
            hero.update_stat_mods(rarity = 2)
        elif reaction.emoji == EmojiLib.get(Rarity.THREE):
            hero.update_stat_mods(rarity = 3)
        elif reaction.emoji == EmojiLib.get(Rarity.FOUR ):
            hero.update_stat_mods(rarity = 4)
        elif reaction.emoji == EmojiLib.get(Rarity.FIVE ):
            hero.update_stat_mods(rarity = 5)
        elif reaction.emoji == '➕':
            hero.update_stat_mods(merges = hero.merges + 1)
        elif reaction.emoji == '➖':
            hero.update_stat_mods(merges = hero.merges - 1)
        elif reaction.emoji == '💾':
            embed.set_footer(text = 'Coming Soon!',
                             icon_url = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/146/floppy-disk_1f4be.png')
        elif reaction.emoji == '👁':
            embed.set_author(name=str(hero.id))
        else: return
        embed = self.format_stats(hero, embed, data[0])
        await bot_msg.edit(embed = embed)
        if bot_msg.channel.permissions_for(bot_msg.author).manage_messages:
            await bot_msg.remove_reaction(reaction, user)



    def format_hero_skills(self, hero, embed, zoom_state):
        embed.title = (f'{hero.name}: {hero.epithet} '
                       f'{EmojiLib.get(hero.weapon_type)}'
                       f'{EmojiLib.get(hero.move_type)}')

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
            weapon    = next((s[0] for s in hero.weapon [::-1]
                              if s[1] <= hero.rarity), Skill.EMPTY_WEAPON )
            assist    = next((s[0] for s in hero.assist [::-1]
                              if s[1] <= hero.rarity), Skill.EMPTY_ASSIST )
            special   = next((s[0] for s in hero.special[::-1]
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
        embed.description = f'{desc_rarity}\n\n{desc_skills}'
        embed.add_field(name=embed.title, value=embed.description, inline=False)
        embed.title=''
        embed.description=''
        
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
        zoom_state = False
        this_hero = copy(UnitLib.get_hero(tokens[0]))
        hero_embed = discord.Embed()
        hero_embed = self.format_hero_skills(this_hero, hero_embed, zoom_state)
        
        hero_embed.set_thumbnail(url='https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{}/Face.png'
                                 .format(this_hero.id))

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
        print(reaction.emoji)
        if   reaction.emoji == '🔍':
            data[0] = not data[0]
        elif reaction.emoji == EmojiLib.get(Rarity.ONE  ):
            hero.update_stat_mods(rarity = 1)
        elif reaction.emoji == EmojiLib.get(Rarity.TWO  ):
            hero.update_stat_mods(rarity = 2)
        elif reaction.emoji == EmojiLib.get(Rarity.THREE):
            hero.update_stat_mods(rarity = 3)
        elif reaction.emoji == EmojiLib.get(Rarity.FOUR ):
            hero.update_stat_mods(rarity = 4)
        elif reaction.emoji == EmojiLib.get(Rarity.FIVE ):
            hero.update_stat_mods(rarity = 5)
        elif reaction.emoji == '💾':
            embed.set_footer(text = 'Coming Soon!',
                             icon_url = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/146/floppy-disk_1f4be.png')
        elif reaction.emoji == '👁':
            embed.set_author(name=str(hero.id))
        else: return
        embed = self.format_hero_skills(hero, embed, data[0])
        await bot_msg.edit(embed = embed)
        if bot_msg.channel.permissions_for(bot_msg.author).manage_messages:
            await bot_msg.remove_reaction(reaction, user)



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
                    skill.eff_armor,
                    skill.eff_cavalry,
                    skill.eff_flier,
                    skill.eff_magic,
                    skill.eff_dragon
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
        else: weapon_desc = None

        prereq = (' '.join(['**Requires:**',
                            str(skill.prereq1.icon), skill.prereq1.name,
                            'or', str(skill.prereq2.icon), skill.prereq2.name])
                  if skill.prereq2
                  else
                  ' '.join(('**Requires:**', str(skill.prereq1.icon), skill.prereq1.name))
                  if skill.prereq1
                  else None
                  ) if not skill.exclusive else (
                        '_This skill can only be equipped by its original unit._')

        restrictions = None
        if skill.type != SkillType.WEAPON:
            if skill.is_staff:
                restrictions = "_This skill can only be equipped by staff users._"
            else:
                restrict_list = ['**Cannot use:** ']
                if not skill.infantry: restrict_list.append(str(EmojiLib.get(MoveType.INFANTRY      )))
                if not skill.armor   : restrict_list.append(str(EmojiLib.get(MoveType.ARMOR         )))
                if not skill.cavalry : restrict_list.append(str(EmojiLib.get(MoveType.CAVALRY       )))
                if not skill.flier   : restrict_list.append(str(EmojiLib.get(MoveType.FLIER         )))
                if not skill.r_sword : restrict_list.append(str(EmojiLib.get(UnitWeaponType.R_SWORD )))
                if not skill.r_tome  : restrict_list.append(str(EmojiLib.get(UnitWeaponType.R_TOME  )))
                if not skill.r_dagger: restrict_list.append(str(EmojiLib.get(UnitWeaponType.R_BOW   )))
                if not skill.r_bow   : restrict_list.append(str(EmojiLib.get(UnitWeaponType.R_DAGGER)))
                if not skill.r_breath: restrict_list.append(str(EmojiLib.get(UnitWeaponType.R_BREATH)))
                if not skill.b_lance : restrict_list.append(str(EmojiLib.get(UnitWeaponType.B_LANCE )))
                if not skill.b_bow   : restrict_list.append(str(EmojiLib.get(UnitWeaponType.B_TOME  )))
                if not skill.b_dagger: restrict_list.append(str(EmojiLib.get(UnitWeaponType.B_BOW   )))
                if not skill.b_tome  : restrict_list.append(str(EmojiLib.get(UnitWeaponType.B_DAGGER)))
                if not skill.b_breath: restrict_list.append(str(EmojiLib.get(UnitWeaponType.B_BREATH)))
                if not skill.g_axe   : restrict_list.append(str(EmojiLib.get(UnitWeaponType.G_AXE   )))
                if not skill.g_bow   : restrict_list.append(str(EmojiLib.get(UnitWeaponType.G_TOME  )))
                if not skill.g_dagger: restrict_list.append(str(EmojiLib.get(UnitWeaponType.G_BOW   )))
                if not skill.g_tome  : restrict_list.append(str(EmojiLib.get(UnitWeaponType.G_DAGGER)))
                if not skill.g_breath: restrict_list.append(str(EmojiLib.get(UnitWeaponType.G_BREATH)))
                if not skill.c_bow   : restrict_list.append(str(EmojiLib.get(UnitWeaponType.C_BOW   )))
                if not skill.c_dagger: restrict_list.append(str(EmojiLib.get(UnitWeaponType.C_DAGGER)))
                if not skill.c_staff : restrict_list.append(str(EmojiLib.get(UnitWeaponType.C_STAFF )))
                if not skill.c_breath: restrict_list.append(str(EmojiLib.get(UnitWeaponType.C_BREATH)))
                if len(restrict_list) > 1:
                    restrictions = ''.join(restrict_list)

        sp = f'**SP:** {skill.sp}'

        if (skill.type == SkillType.WEAPON and not skill.exclusive
            and ((skill.tier <= 2 and not skill.is_staff) or skill.tier <= 1)):
            learnable = 'Basic weapon available to most eligible heroes.'
        elif skill.type == SkillType.ASSIST and skill.is_staff:
            learnable = 'Basic assist available to all staff-users.'
        elif reduce(lambda x, y: x + len(y), skill.learnable[1:], 0) > 20:
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
                        (lambda x, y: x + 1 if y.exclusive else x),
                        skill.postreq,
                        0
                )
                # optimize note?
                postreq_list = (', '.join(filter(None, [
                        f'{postreq.icon} {postreq.name}'
                        if not postreq.exclusive else None
                        for postreq in skill.postreq
                ]))
                if len(skill.postreq) - prf_postreq_count < 10
                else ', '.join(filter(None, [
                        f'{postreq.name}'
                        if not postreq.exclusive else None
                        for postreq in skill.postreq
                ])))

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
                generic_refines = '\n'.join(filter(None, [
                        f'{refine.icon}: {refine.description}'
                        if refine else None
                        for refine in [
                                skill.refine_staff1,
                                skill.refine_staff2,
                                skill.refine_atk,
                                skill.refine_spd,
                                skill.refine_def,
                                skill.refine_res
                        ]
                ]))
            else:
                generic_refines = ', '.join(filter(None, [
                        str(refine.icon) if refine else None
                        for refine in [
                                skill.refine_staff1,
                                skill.refine_staff2,
                                skill.refine_atk,
                                skill.refine_spd,
                                skill.refine_def,
                                skill.refine_res
                        ]
                ]))

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
        this_skill = UnitLib.get_skill(tokens[0])
        skill_embed = discord.Embed()
        zoom_state = False
        self.format_skill(this_skill, skill_embed, zoom_state)
        botreply = await message.channel.send(embed=skill_embed)
        self.register_reactable(botreply, message, message.author, [this_skill], CMDType.SKILL, skill_embed, [zoom_state])
        await botreply.add_reaction('🔍')
        await botreply.add_reaction('⬆')
        await botreply.add_reaction('⬇')



    async def react_skill(self, reaction, bot_msg, user_msg, user, skill, cmd_type, embed, data):
        manage_msg = bot_msg.channel.permissions_for(bot_msg.author).manage_messages

        if reaction.emoji == '🔍':
            data[0] = not data[0]
            if manage_msg: await bot_msg.remove_reaction(reaction, user)
        elif reaction.emoji == '⬆':
            skill[0] = skill[0].postreq[0] if len(skill[0].postreq) > 0 else skill[0]
            if manage_msg: await bot_msg.remove_reaction(reaction, user)
        elif reaction.emoji == '⬇':
            skill[0] = skill[0].prereq1 if skill[0].prereq1 else skill[0]
            if manage_msg: await bot_msg.remove_reaction(reaction, user)
        elif reaction.emoji == '👁':
            embed.set_author(name=str(skill[0].id))
            if manage_msg: await bot_msg.remove_reaction(reaction, user)
        else: return
        embed = self.format_skill(skill[0], embed, data[0])
        await bot_msg.edit(embed = embed)



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

        #TODO: kind of gross line, also investigate if RE or map is faster here?

        if   lower_message.startswith('hero') or lower_message.startswith('unit'):
            tokens = [s.strip() for s in lower_message.split(' ', 1)[1].split(',')]
            await self.cmd_hero(message, tokens)
        elif lower_message.startswith('stat'):
            tokens = [s.strip() for s in lower_message.split(' ', 1)[1].split(',')]
            await self.cmd_stats(message, tokens)
        elif lower_message.startswith('skills'):
            tokens = [s.strip() for s in lower_message.split(' ', 1)[1].split(',')]
            await self.cmd_hero_skills(message, tokens)
        elif lower_message.startswith('skill'):
            tokens = [s.strip() for s in lower_message.split(' ', 1)[1].split(',')]
            await self.cmd_skill(message, tokens)

        #debug commands

        if (lower_message.startswith('emojis')
            and (message.author.id == 151913154803269633
                 or message.author.id == 196379129472352256)):
            emojilisttemp = sorted(self.emojis, key=lambda q: (q.name))
            for e in emojilisttemp:
                print(e.name)
                await message.channel.send(str(e) + str(e.id))

        if lower_message.startswith('whoami'):
            await message.channel.send(f"You're <{message.author.id}>!")

        if lower_message.startswith('test'):
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



    async def on_reaction_add(self, reaction, user):
        if (reaction.message.author != client.user
            or user == client.user
            or reaction.message.id not in self.reactable_library): return
        print('reactable ok')

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
