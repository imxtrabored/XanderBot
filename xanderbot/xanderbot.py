import discord
import asyncio

from copy import copy
from collections import namedtuple
from enum import Enum

from feh.emojilib import EmojiLib
from feh.hero import Hero, Color, UnitWeaponType, MoveType
from feh.hero import LegendElement, Stat
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
        embed.title = ''.join((
            hero.name,
            ': ',
            hero.epithet,
            ' ',
            str(EmojiLib.get(hero.weapon_type)),
            str(EmojiLib.get(hero.move_type))
        ))
        if   hero.rarity == 5: desc_rarity = str(EmojiLib.get('Rarity_5')) * 5
        elif hero.rarity == 4: desc_rarity = str(EmojiLib.get('Rarity_4')) * 4
        elif hero.rarity == 3: desc_rarity = str(EmojiLib.get('Rarity_3')) * 3
        elif hero.rarity == 2: desc_rarity = str(EmojiLib.get('Rarity_2')) * 2
        else                 : desc_rarity = str(EmojiLib.get('Rarity_1')) * 1
        desc_level = ''.join((desc_rarity, '     LV. ', str(hero.level), '+', str(hero.merges)))
        BST = ''.join(('BST: ', str(hero.max_total)))
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
            stat_emojis = ' · '.join([
                str(EmojiLib.get(Stat.HP )),
                str(EmojiLib.get(Stat.ATK)),
                str(EmojiLib.get(Stat.SPD)),
                str(EmojiLib.get(Stat.DEF)),
                str(EmojiLib.get(Stat.RES)),
                BST
            ])
            lvl1_stats = ' |'.join([
                str(hero.lv1_hp ).rjust(2),
                str(hero.lv1_atk).rjust(2),
                str(hero.lv1_spd).rjust(2),
                str(hero.lv1_def).rjust(2),
                str(hero.lv1_res).rjust(2)
            ])
            superboons = [
                ' ' if x == 0 else '+' if x > 0 else '-'
                for x in hero.get_boons_banes()
            ]
            max_stats = ''.join([
                str(hero.max_hp ).rjust(2), superboons[0], '|',
                str(hero.max_atk).rjust(2), superboons[1], '|', 
                str(hero.max_spd).rjust(2), superboons[2], '|',
                str(hero.max_def).rjust(2), superboons[3], '|',
                str(hero.max_res).rjust(2), superboons[4]
            ])
            desc_stat = '\n'.join((stat_emojis, '```', lvl1_stats, max_stats, '```'))

        embed.clear_fields()
        embed.description = '\n'.join((desc_level + '\n', desc_stat))
        embed.add_field(name=embed.title, value=embed.description, inline=False)
        embed.title=''
        embed.description=''
        
        if zoom_state:
            embed.add_field(name='Level 1 Stats', value=lv1_stats, inline=True)
            embed.add_field(name='Level 40 Stats', value=max_stats, inline=True)
        return embed



    async def cmd_stats(self, message, tokens):
        zoom_state = False
        this_hero = copy(UnitLib.get_hero(tokens[0]))
        hero_embed = discord.Embed()
        hero_embed = self.format_stats(this_hero, hero_embed, zoom_state)
        
        hero_embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{this_hero.id}/Face.png')

        botreply = await message.channel.send(embed=hero_embed)
        self.register_reactable(botreply, message, message.author, this_hero, CMDType.HERO_STATS, hero_embed, [zoom_state])
        await botreply.add_reaction('🔍')
        await botreply.add_reaction(EmojiLib.get('Rarity_1'))
        await botreply.add_reaction(EmojiLib.get('Rarity_2'))
        await botreply.add_reaction(EmojiLib.get('Rarity_3'))
        await botreply.add_reaction(EmojiLib.get('Rarity_4'))
        await botreply.add_reaction(EmojiLib.get('Rarity_5'))
        await botreply.add_reaction('➕')
        await botreply.add_reaction('➖')



    async def react_stats(self, reaction, bot_msg, user_msg, user, hero, cmd_type, embed, data):
        if   reaction.emoji == '🔍':
            data[0] = not data[0]
        elif reaction.emoji == EmojiLib.get('Rarity_1'):
            hero.update_stat_mods(rarity = 1)
        elif reaction.emoji == EmojiLib.get('Rarity_2'):
            hero.update_stat_mods(rarity = 2)
        elif reaction.emoji == EmojiLib.get('Rarity_3'):
            hero.update_stat_mods(rarity = 3)
        elif reaction.emoji == EmojiLib.get('Rarity_4'):
            hero.update_stat_mods(rarity = 4)
        elif reaction.emoji == EmojiLib.get('Rarity_5'):
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
        embed.title = ''.join((
            hero.name,
            ': ',
            hero.epithet,
            ' ',
            str(EmojiLib.get(hero.weapon_type)),
            str(EmojiLib.get(hero.move_type))
        ))
        if   hero.rarity == 5: desc_rarity = str(EmojiLib.get('Rarity_5')) * 5
        elif hero.rarity == 4: desc_rarity = str(EmojiLib.get('Rarity_4')) * 4
        elif hero.rarity == 3: desc_rarity = str(EmojiLib.get('Rarity_3')) * 3
        elif hero.rarity == 2: desc_rarity = str(EmojiLib.get('Rarity_2')) * 2
        else                 : desc_rarity = str(EmojiLib.get('Rarity_1')) * 1

        desc_skills = ''
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
            weapon    = next((s[0].name for s in hero.weapon   [::-1] if s[1] <= hero.rarity), 'None')
            assist    = next((s[0].name for s in hero.assist   [::-1] if s[1] <= hero.rarity), 'None')
            special   = next((s[0].name for s in hero.special  [::-1] if s[1] <= hero.rarity), 'None')
            passive_a = next((str(s[0].icon) + str(s[0].rank) for s in hero.passive_a[::-1] if s[1] <= hero.rarity), str(EmojiLib.get(SkillType.PASSIVE_A)))
            passive_b = next((str(s[0].icon) + str(s[0].rank) for s in hero.passive_b[::-1] if s[1] <= hero.rarity), str(EmojiLib.get(SkillType.PASSIVE_B)))
            passive_c = next((str(s[0].icon) + str(s[0].rank) for s in hero.passive_c[::-1] if s[1] <= hero.rarity), str(EmojiLib.get(SkillType.PASSIVE_C)))
            desc_skills = (
                f'{str(EmojiLib.get(SkillType.WEAPON ))}{weapon }\n'
                f'{str(EmojiLib.get(SkillType.ASSIST ))}{assist }\n'
                f'{str(EmojiLib.get(SkillType.SPECIAL))}{special}\n\n'
                f'{passive_a} · {passive_b} · {passive_c}'
            )
            print(EmojiLib.get(SkillType.WEAPON ))

        embed.clear_fields()
        embed.description = '\n'.join((desc_rarity + '\n', desc_skills))
        embed.add_field(name=embed.title, value=embed.description, inline=False)
        embed.title=''
        embed.description=''
        
        if zoom_state:
            embed.add_field(name='Level 1 Stats', value=lv1_stats, inline=True)
            embed.add_field(name='Level 40 Stats', value=max_stats, inline=True)
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
        self.register_reactable(botreply, message, message.author, this_hero, CMDType.HERO_SKILLS, hero_embed, [zoom_state])
        await botreply.add_reaction('🔍')
        await botreply.add_reaction(EmojiLib.get('Rarity_1'))
        await botreply.add_reaction(EmojiLib.get('Rarity_2'))
        await botreply.add_reaction(EmojiLib.get('Rarity_3'))
        await botreply.add_reaction(EmojiLib.get('Rarity_4'))
        await botreply.add_reaction(EmojiLib.get('Rarity_5'))



    async def react_hero_skills(self, reaction, bot_msg, user_msg, user, hero, cmd_type, embed, data):
        print(reaction.emoji)
        if   reaction.emoji == '🔍':
            data[0] = not data[0]
        elif reaction.emoji == EmojiLib.get('Rarity_1'):
            hero.update_stat_mods(rarity = 1)
        elif reaction.emoji == EmojiLib.get('Rarity_2'):
            hero.update_stat_mods(rarity = 2)
        elif reaction.emoji == EmojiLib.get('Rarity_3'):
            hero.update_stat_mods(rarity = 3)
        elif reaction.emoji == EmojiLib.get('Rarity_4'):
            hero.update_stat_mods(rarity = 4)
        elif reaction.emoji == EmojiLib.get('Rarity_5'):
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
        title = ' '.join((str(skill.icon), skill.name, ' · ',
                          (str(EmojiLib.get(skill.weapon_type)) if skill.weapon_type
                           else str(EmojiLib.get(skill.type))),
                          (str(EmojiLib.get(SkillType.PASSIVE_SEAL))
                           if skill.type != SkillType.PASSIVE_SEAL and skill.is_seal
                           else '')))
        weapon_desc = (' '.join(('Mt:', str(skill.disp_atk),
                                 'Rng:', str(skill.range)))
                       if (skill.type == SkillType.WEAPON or skill.type == SkillType.WEAPON_REFINED) else None)

        s_type = ''.join(('Type: ',
                          (str(EmojiLib.get(skill.weapon_type)) if skill.weapon_type
                           else str(EmojiLib.get(skill.type))),
                          (str(EmojiLib.get(SkillType.PASSIVE_SEAL))
                           if skill.type != SkillType.PASSIVE_SEAL and skill.is_seal
                           else '')
                          ))

        prereq = (' '.join(('**Requires:**',
                            str(skill.prereq1.icon), skill.prereq1.name,
                            'or', str(skill.prereq2.icon), skill.prereq2.name))
                  if skill.prereq2
                  else
                  ' '.join(('**Requires:**', str(skill.prereq1.icon), skill.prereq1.name))
                  if skill.prereq1
                  else None
                  ) if not skill.exclusive else 'This skill can only be equipped by its original unit.'

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
        '''description += '**Promotes into:** '
        for s in skill.postreq: description += s.name'''
        sp = '**SP: ** ' + str(skill.sp)
        embed.clear_fields()
        embed.add_field(name=title,
                              value='\n'.join(
                                  filter(None,(weapon_desc,
                                               skill.description,
                                               #s_type,
                                               prereq,
                                               restrictions,
                                               sp))),
                              inline=False)

        if skill.refinable:
            refined_title = 'Weapon Refinery'
            refined_skill_str = None
            if skill.refined_version:
                refined_skill = skill.refined_version
                refined_title = ''.join(('Weapon Refinery\n', str(refined_skill.icon), ' Refined ', skill.name))
                refined_w_desc = (' '.join(('Mt:', str(refined_skill.disp_atk),
                                            'Rng:', str(refined_skill.range)))
                                if refined_skill.type == SkillType.WEAPON or refined_skill.type == SkillType.WEAPON_REFINED
                                else None)
                refined_skill_str = '\n'.join(filter(None, (refined_w_desc, refined_skill.description)))

            refine_eff = (': '.join((str(skill.refine_eff.icon), skill.refine_eff.description))
                          if skill.refine_eff else None)
            general_refine_list = []
            if skill.refine_staff1: general_refine_list.append(str(skill.refine_staff1.icon))
            if skill.refine_staff2: general_refine_list.append(str(skill.refine_staff2.icon))
            if skill.refine_atk   : general_refine_list.append(str(skill.refine_atk.   icon))
            if skill.refine_spd   : general_refine_list.append(str(skill.refine_spd.   icon))
            if skill.refine_def   : general_refine_list.append(str(skill.refine_def.   icon))
            if skill.refine_res   : general_refine_list.append(str(skill.refine_res.   icon))
            generic_refines = ', '.join(general_refine_list)

            embed.add_field(name=refined_title,
                                  value='\n'.join(filter(None, (refined_skill_str,
                                                                '**Refine options:**',
                                                                refine_eff,
                                                                generic_refines))),
                                  inline=False)
        print(skill.icon.id)
        if skill.type == SkillType.WEAPON or skill.type == SkillType.WEAPON_REFINED:
                    embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/skills/{skill.id}.png')
        else: embed.set_thumbnail(url=f'https://cdn.discordapp.com/emojis/{skill.icon.id}.png')

        return embed



    async def cmd_skill(self, message, tokens):
        this_skill = self.unit_library.get_skill(tokens[0])
        skill_embed = discord.Embed()
        zoom_state = False
        self.format_skill(this_skill, skill_embed, zoom_state)
        botreply = await message.channel.send(embed=skill_embed)
        self.register_reactable(botreply, message, message.author, [this_skill], CMDType.SKILL, skill_embed, [zoom_state])
        await botreply.add_reaction('🔍')
        await botreply.add_reaction('⬆')
        await botreply.add_reaction('⬇')



    async def react_skill(self, reaction, bot_msg, user_msg, user, skill, cmd_type, embed, data):
        if reaction.emoji == '🔍':
            data[0] = not data[0]
        elif reaction.emoji == '⬆':
            skill[0] = skill[0].postreq[0] if len(skill[0].postreq) > 0 else skill[0]
        elif reaction.emoji == '⬇':
            skill[0] = skill[0].prereq1 if skill[0].prereq1 else skill[0]
        elif reaction.emoji == '👁':
            embed.set_author(name=str(skill[0].id))
        else: return
        embed = self.format_skill(skill[0], embed, data[0])
        await bot_msg.edit(embed = embed)
        if bot_msg.channel.permissions_for(bot_msg.author).manage_messages:
            await bot_msg.remove_reaction(reaction, user)



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
        tokens = [s.strip() for s in lower_message.split(' ', 1)[1].split(',')]

        if   lower_message.startswith('hero') or lower_message.startswith('unit'):
            await self.cmd_hero(message, tokens)
        elif lower_message.startswith('stat'):
            await self.cmd_stats(message, tokens)
        elif lower_message.startswith('skills'):
            await self.cmd_hero_skills(message, tokens)
        elif lower_message.startswith('skill'):
            await self.cmd_skill(message, tokens)

        #debug commands

        if lower_message.startswith('2emotes'):
            print("asdfasdf")
            emojilisttemp = sorted(self.emojis, key=lambda q: (q.name))
            for e in emojilisttemp:
                print(e.name)
                await message.channel.send(str(e) + str(e.id))

        if lower_message.startswith('whoami'):
            await message.channel.send("You're <" + str(message.author.id) + '>!')

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
