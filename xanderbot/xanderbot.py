import discord
import asyncio

from copy import copy
from collections import namedtuple
from enum import Enum

from emojilib import EmojiLib
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



    async def forget_reactable(self, bot_msg):
        try:
            await asyncio.sleep(20)
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
        this_hero = self.unit_library.unit_list[self.unit_library.unit_names.get(tokens[0])]
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
        this_hero = copy(self.unit_library.unit_list[self.unit_library.unit_names.get(tokens[0])])
        hero_embed = discord.Embed()
        hero_embed = self.format_stats(this_hero, hero_embed, zoom_state)
        
        hero_embed.set_thumbnail(url='https://raw.githubusercontent.com/Rot8erConeX/EliseBot/master/EliseBot/FEHArt/Xander/Face_FC.png')

        botreply = await message.channel.send(embed=hero_embed)
        self.register_reactable(botreply, message, message.author, this_hero, CMDType.HERO_STATS, hero_embed, [zoom_state])
        await botreply.add_reaction('🔍')
        await botreply.add_reaction('⬆')
        await botreply.add_reaction('⬇')
        await botreply.add_reaction('➕')
        await botreply.add_reaction('➖')

        return

        def check(reaction, user):
            if user == message.author:
               if str(reaction.emoji) == '🔍':
                   return True
               elif str(reaction.emoji) == '⬆' or str(reaction.emoji) == '⬇':
                   return True
               elif str(reaction.emoji) == '➕' or str(reaction.emoji) == '➖':
                   return True
            return False
        while(True):
            try:
                reaction, user = await client.wait_for('reaction_add', check=check, timeout=150.0)
            except asyncio.TimeoutError:
                #maybe remove bot reacts
                return
            else:
                if reaction.emoji == '🔍':
                    zoom_state = not zoom_state
                    if zoom_state:
                        lv1_stats, max_stats = large_stat(this_hero)
                        hero_embed.description = description + desc_rarity + desc_merges
                        hero_embed.clear_fields()
                        hero_embed.add_field(name='Level 1 Stats', value=lv1_stats)
                        hero_embed.add_field(name='Level 40 Stats', value=max_stats)
                        await botreply.edit(embed=hero_embed)
                    else:
                        hero_embed.description = description + desc_rarity + desc_merges + mini_stat(this_hero)
                        hero_embed.clear_fields()
                        await botreply.edit(embed=hero_embed)
                    if message.channel.permissions_for(botreply.author).manage_messages:
                        await botreply.remove_reaction('🔍', user)
                elif reaction.emoji == '⬆':
                    await this_hero.update_stat_mods(rarity=this_hero.rarity + 1)
                    desc_rarity = ''
                    for i in range(this_hero.rarity):
                        desc_rarity += 'star'
                    desc_rarity += '\n'
                    if zoom_state:
                        lv1_stats, max_stats = large_stat(this_hero)
                        hero_embed.description = description + desc_rarity + desc_merges
                        hero_embed.clear_fields()
                        hero_embed.add_field(name='Level 1 Stats', value=lv1_stats)
                        hero_embed.add_field(name='Level 40 Stats', value=max_stats)
                        await botreply.edit(embed=hero_embed)
                    else:
                        hero_embed.description = description + desc_rarity + desc_merges + mini_stat(this_hero)
                        hero_embed.clear_fields()
                        await botreply.edit(embed=hero_embed)
                    if message.channel.permissions_for(botreply.author).manage_messages:
                        await botreply.remove_reaction('⬆', user)
                elif reaction.emoji == '⬇':
                    await this_hero.update_stat_mods(rarity=this_hero.rarity - 1)
                    desc_rarity = ''
                    for i in range(this_hero.rarity):
                        desc_rarity += 'star'
                    desc_rarity += '\n'
                    if zoom_state:
                        lv1_stats, max_stats = large_stat(this_hero)
                        hero_embed.description = description + desc_rarity + desc_merges
                        hero_embed.clear_fields()
                        hero_embed.add_field(name='Level 1 Stats', value=lv1_stats)
                        hero_embed.add_field(name='Level 40 Stats', value=max_stats)
                        await botreply.edit(embed=hero_embed)
                    else:
                        hero_embed.description = description + desc_rarity + desc_merges + mini_stat(this_hero)
                        hero_embed.clear_fields()
                        await botreply.edit(embed=hero_embed)
                    if message.channel.permissions_for(botreply.author).manage_messages:
                        await botreply.remove_reaction('⬇', user)
                elif reaction.emoji == '➕':
                    await this_hero.update_stat_mods(merges=this_hero.merges + 1)
                    desc_merges = 'Merges: ' + str(this_hero.merges)+ '\n'
                    if zoom_state:
                        lv1_stats, max_stats = large_stat(this_hero)
                        hero_embed.description = description + desc_rarity + desc_merges
                        hero_embed.clear_fields()
                        hero_embed.add_field(name='Level 1 Stats', value=lv1_stats)
                        hero_embed.add_field(name='Level 40 Stats', value=max_stats)
                        await botreply.edit(embed=hero_embed)
                    else:
                        hero_embed.description = description + desc_rarity + desc_merges + mini_stat(this_hero)
                        hero_embed.clear_fields()
                        await botreply.edit(embed=hero_embed)
                    if message.channel.permissions_for(botreply.author).manage_messages:
                        await botreply.remove_reaction('➕', user)
                elif reaction.emoji == '➖':
                    await this_hero.update_stat_mods(merges = this_hero.merges - 1)
                    desc_merges = 'Merges: ' + str(this_hero.merges)+ '\n'
                    if zoom_state:
                        lv1_stats, max_stats = large_stat(this_hero)
                        hero_embed.description = description + desc_rarity + desc_merges
                        hero_embed.clear_fields()
                        hero_embed.add_field(name='Level 1 Stats', value=lv1_stats)
                        hero_embed.add_field(name='Level 40 Stats', value=max_stats)
                        await botreply.edit(embed=hero_embed)
                    else:
                        hero_embed.description = description + desc_rarity + desc_merges + mini_stat(this_hero)
                        hero_embed.clear_fields()
                        await botreply.edit(embed=hero_embed)
                    if message.channel.permissions_for(botreply.author).manage_messages:
                        await botreply.remove_reaction('➖', user)



    async def react_stats(self, reaction, bot_msg, user_msg, user, hero, cmd_type, embed, data):
        if reaction.emoji == '🔍':
            data[0] = not data[0]
            embed = self.format_stats(hero, embed, data[0])
            await bot_msg.edit(embed = embed)
            if bot_msg.channel.permissions_for(bot_msg.author).manage_messages:
                await bot_msg.remove_reaction('🔍', user)




    async def cmd_skill(self, message, tokens):
        this_skill = self.unit_library.skill_list[self.unit_library.skill_names.get(tokens[0])]
        skill_embed = discord.Embed(title = this_skill.name)
        description = ""
        if this_skill.type == SkillType.WEAPON or this_skill.type == SkillType.WEAPON_REFINED:
            description += this_skill.weapon_type.name + ' Mt: ' + str(this_skill.disp_atk) + ' Rng: ' + str(this_skill.range)
        else: description += this_skill.type.name
        description += '\n'
        if this_skill.description: description += this_skill.description + '\n'
        if this_skill.prereq1:
            description += '**Requires: ** '
            description += self.unit_library.skill_list[this_skill.prereq1].name
            if this_skill.prereq2:
                description += ', '
                description += self.unit_library.skill_list[this_skill.prereq2].name

        if this_skill.type != SkillType.WEAPON:
            if this_skill.is_staff:
                restrictions = "\nThis skill can only be equipped by staff users."
                description += restrictions
            else:
                restrictions = []
                if not this_skill.infantry: restrictions.append(str(EmojiLib.get(MoveType.INFANTRY      )))
                if not this_skill.armor   : restrictions.append(str(EmojiLib.get(MoveType.ARMOR         )))
                if not this_skill.cavalry : restrictions.append(str(EmojiLib.get(MoveType.CAVALRY       )))
                if not this_skill.flier   : restrictions.append(str(EmojiLib.get(MoveType.FLIER         )))
                if not this_skill.r_sword : restrictions.append(str(EmojiLib.get(UnitWeaponType.R_SWORD )))
                if not this_skill.r_tome  : restrictions.append(str(EmojiLib.get(UnitWeaponType.R_TOME  )))
                if not this_skill.r_dagger: restrictions.append(str(EmojiLib.get(UnitWeaponType.R_BOW   )))
                if not this_skill.r_bow   : restrictions.append(str(EmojiLib.get(UnitWeaponType.R_DAGGER)))
                if not this_skill.r_breath: restrictions.append(str(EmojiLib.get(UnitWeaponType.R_BREATH)))
                if not this_skill.b_lance : restrictions.append(str(EmojiLib.get(UnitWeaponType.B_LANCE )))
                if not this_skill.b_bow   : restrictions.append(str(EmojiLib.get(UnitWeaponType.B_TOME  )))
                if not this_skill.b_dagger: restrictions.append(str(EmojiLib.get(UnitWeaponType.B_BOW   )))
                if not this_skill.b_tome  : restrictions.append(str(EmojiLib.get(UnitWeaponType.B_DAGGER)))
                if not this_skill.b_breath: restrictions.append(str(EmojiLib.get(UnitWeaponType.B_BREATH)))
                if not this_skill.g_axe   : restrictions.append(str(EmojiLib.get(UnitWeaponType.G_AXE   )))
                if not this_skill.g_bow   : restrictions.append(str(EmojiLib.get(UnitWeaponType.G_TOME  )))
                if not this_skill.g_dagger: restrictions.append(str(EmojiLib.get(UnitWeaponType.G_BOW   )))
                if not this_skill.g_tome  : restrictions.append(str(EmojiLib.get(UnitWeaponType.G_DAGGER)))
                if not this_skill.g_breath: restrictions.append(str(EmojiLib.get(UnitWeaponType.G_BREATH)))
                if not this_skill.c_bow   : restrictions.append(str(EmojiLib.get(UnitWeaponType.C_BOW   )))
                if not this_skill.c_dagger: restrictions.append(str(EmojiLib.get(UnitWeaponType.C_DAGGER)))
                if not this_skill.c_staff : restrictions.append(str(EmojiLib.get(UnitWeaponType.C_STAFF )))
                if not this_skill.c_breath: restrictions.append(str(EmojiLib.get(UnitWeaponType.C_BREATH)))
                if restrictions != '': description += ''.join(['\n**Cannot use:** '].append(restrictions))
        '''description += '\n**Promotes into:** '
        for s in this_skill.postreq: description += s.name'''
        description += '\n**SP: ** ' + str(this_skill.sp)

        if this_skill.refinable:
            description += '\n***Refinery***\n'
            if this_skill.refined_version:
                refined_skill = self.unit_library.skill_list[this_skill.refined_version]
                description += '**Refined ' + this_skill.name + '**\n'
                if refined_skill.type == SkillType.WEAPON or refined_skill.type == SkillType.WEAPON_REFINED:
                    description += refined_skill.weapon_type.name + ' Mt: ' + str(refined_skill.disp_atk) + ' Rng: ' + str(refined_skill.range)
                else: description += refined_skill.type.name
                description += '\n'
                if refined_skill.description: description += refined_skill.description + '\n'
            if this_skill.refine_eff:
                description += 'Eff: ' + self.unit_library.skill_list[this_skill.refine_eff].description + '\n'
            description += 'Generic refines: '
            if this_skill.refine_atk:
                description += 'atk, '
            if this_skill.refine_spd:
                description += 'spd, '
            if this_skill.refine_def:
                description += 'def, '
            if this_skill.refine_res:
                description += 'res, '

        skill_embed.description = description

        await message.channel.send(embed=skill_embed)
        return



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

        if lower_message.startswith('hero') or lower_message.startswith('unit'):
            await self.cmd_hero(message, tokens)
        if lower_message.startswith('stat'):
            await self.cmd_stats(message, tokens)
        if lower_message.startswith('skill'):
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



client = XanderBotClient()
client.run(client.token)
