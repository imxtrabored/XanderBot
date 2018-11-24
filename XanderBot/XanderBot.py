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
        this_hero.update_rarity(4)
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
        if len(this_hero.skills.weapon) > 0:
            skills = ''
            for counter, skill in enumerate(this_hero.skills.weapon):
                if skill != None:
                    skills += skill.name + ' ' + str(counter) + 'star\n'
            if skills == '': skills = 'None'
            hero_embed.add_field(name='Weapons', value=skills)
        if len(this_hero.skills.assist) > 0:
            skills = ''
            for counter, skill in enumerate(this_hero.skills.assist):
                if skill != None:
                    skills += skill.name + ' ' + str(counter) + 'star\n'
            if skills == '': skills = 'None'
            hero_embed.add_field(name='Assists', value=skills)
        if len(this_hero.skills.special) > 0:
            skills = ''
            for counter, skill in enumerate(this_hero.skills.special):
                if skill != None:
                    skills += skill.name + ' ' + str(counter) + 'star\n'
            if skills == '': skills = 'None'
            hero_embed.add_field(name='Specials', value=skills)
        if len(this_hero.skills.passive_a) > 0:
            skills = ''
            for counter, skill in enumerate(this_hero.skills.passive_a):
                if skill != None:
                    skills += skill.name + ' ' + str(counter) + 'star\n'
            if skills == '': skills = 'None'
            hero_embed.add_field(name='Passive A', value=skills)
        if len(this_hero.skills.passive_b) > 0:
            skills = ''
            for counter, skill in enumerate(this_hero.skills.passive_b):
                if skill != None:
                    skills += skill.name + ' ' + str(counter) + 'star\n'
            if skills == '': skills = 'None'
            hero_embed.add_field(name='Passive B', value=skills)
        if len(this_hero.skills.passive_c) > 0:
            skills = ''
            for counter, skill in enumerate(this_hero.skills.passive_c):
                if skill != None:
                    skills += skill.name + ' ' + str(counter) + 'star\n'
            if skills == '': skills = 'None'
            hero_embed.add_field(name='Passive C', value=skills)
        await message.channel.send(embed=hero_embed)
        return

    async def cmd_stats(self, message, tokens):
        this_hero = self.library.unit_list[self.library.unit_names.get(tokens[1])]
        hero_embed = discord.Embed(title = this_hero.name + ': ' + this_hero.epithet)
        description = ''

        await message.channel.send(hero_embed)


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
