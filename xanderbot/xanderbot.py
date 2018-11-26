import discord
import asyncio

from feh.hero import Hero, Color, WeaponType, MoveType
from feh.hero import LegendElement, Stat
from feh.unitlib import UnitLib

FILENAME = '../tokens.txt'
file = open (FILENAME, 'r')
token = file.readline().rstrip('\n')
file.close()

class XanderBotClient(discord.Client):

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        print('loading data...')
        self.library = await UnitLib.initialize()
        print('done.')

    async def cmd_hero(self, message, tokens):
        this_hero = self.library.unit_list[self.library.unit_names.get(tokens[1])]
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

    async def cmd_stats(self, message, tokens):
        zoom_state = False
        this_hero = self.library.unit_list[self.library.unit_names.get(tokens[1])]
        hero_embed = discord.Embed(title = this_hero.name + ': ' + this_hero.epithet)
        description = ''
        description += this_hero.color.name + ' ' + this_hero.weapon_type.name + ' ' + this_hero.move_type.name + '\n'
        desc_rarity = ''
        for i in range(this_hero.rarity):
            desc_rarity += 'star'
        desc_rarity += '\n'
        desc_merges = 'Merges: ' + str(this_hero.merges) + '\n'

        def mini_stat(this_hero):
            stat_desc = '```\nhp|at|sp|df|rs\n'
            stat_desc += str(this_hero.lv1_hp ).rjust(2) + '|'
            stat_desc += str(this_hero.lv1_atk).rjust(2) + '|'
            stat_desc += str(this_hero.lv1_spd).rjust(2) + '|'
            stat_desc += str(this_hero.lv1_def).rjust(2) + '|'
            stat_desc += str(this_hero.lv1_res).rjust(2) + '\n'
            stat_desc += str(this_hero.max_hp ).rjust(2) + '|'
            stat_desc += str(this_hero.max_atk).rjust(2) + '|'
            stat_desc += str(this_hero.max_spd).rjust(2) + '|'
            stat_desc += str(this_hero.max_def).rjust(2) + '|'
            stat_desc += str(this_hero.max_res).rjust(2) + '\n```'
            return stat_desc

        def large_stat(this_hero):
            lv1_stats = 'HP: ' + str(this_hero.lv1_hp)
            lv1_stats += '\nAtk: ' + str(this_hero.lv1_atk)
            lv1_stats += '\nSpd: ' + str(this_hero.lv1_spd)
            lv1_stats += '\nDef: ' + str(this_hero.lv1_def)
            lv1_stats += '\nRes: ' + str(this_hero.lv1_res)
            max_stats = 'HP: ' + str(this_hero.max_hp)
            max_stats += '\nAtk: ' + str(this_hero.max_atk)
            max_stats += '\nSpd: ' + str(this_hero.max_spd)
            max_stats += '\nDef: ' + str(this_hero.max_def)
            max_stats += '\nRes: ' + str(this_hero.max_res)
            return lv1_stats, max_stats
        
        hero_embed.description = description + desc_rarity + desc_merges + mini_stat(this_hero)

        botreply = await message.channel.send(embed=hero_embed)
        await botreply.add_reaction('🔍')
        await botreply.add_reaction('⬆')
        await botreply.add_reaction('⬇')
        await botreply.add_reaction('➕')
        await botreply.add_reaction('➖')

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

            


    async def cmd_skill(self, message, tokens):
        this_skill = self.library.skill_list[self.library.skill_names.get(tokens[1])]
        skill_embed = discord.Embed(title = this_skill.name)
        description = this_skill.description + '\n'
        description += '**Requires:** '
        for s in this_skill.prereq: description += s.name
        description += '\n**Promotes into:** '
        for s in this_skill.postreq: description += s.name
        description += '\n**SP cost:** ' + str(this_skill.sp)

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

        tokens = lower_message.split()

        if lower_message.startswith('hero') or lower_message.startswith('unit'):
            await self.cmd_hero(message, tokens)
        if lower_message.startswith('stat'):
            await self.cmd_stats(message, tokens)
        if lower_message.startswith('skill'):
            await self.cmd_skill(message, tokens)

        #debug commands

        if lower_message.startswith('emotes'):
            for e in self.emojis:
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

client = XanderBotClient()
client.run(token)
