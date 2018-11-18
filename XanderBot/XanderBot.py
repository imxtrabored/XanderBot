import discord
import asyncio

from FEH.Hero import Hero, Color, WeaponType, MoveType
from FEH.Hero import LegendElement, LegendBoost

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

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        lowerMessage = message.content.lower()
        if not (lowerMessage.startswith('f?') or lowerMessage.startswith('feh?')):
            return
        if lowerMessage.startswith('f?'):
            lowerMessage = lowerMessage[2:]
        elif lowerMessage.startswith('feh?'):
            lowerMessage = lowerMessage[4:]

        if lowerMessage.startswith('hero') or lowerMessage.startswith('unit'):
            thisHero = await Hero.create('null')
            heroEmbed = discord.Embed(title = thisHero.name + ': ' + thisHero.epithet)
            description = ''
            description += thisHero.color.name + ' ' + thisHero.weaponType.name + ' ' + thisHero.moveType.name + '\n'
            for i in range(thisHero.rarity):
                description += 'star' 
            heroEmbed.description = description
            heroEmbed.colour = discord.Colour.from_rgb(255, 0, 0)
            if len(thisHero.skills.weapon) > 0:
                skills = ''
                for counter, skill in enumerate(thisHero.skills.weapon):
                    if skill != None:
                        skills += skill.name + ' ' + str(counter) + 'star\n'
                if skills == '': skills = 'None'
                heroEmbed.add_field(name='Weapons', value=skills)
            if len(thisHero.skills.assist) > 0:
                skills = ''
                for counter, skill in enumerate(thisHero.skills.assist):
                    if skill != None:
                        skills += skill.name + ' ' + str(counter) + 'star\n'
                if skills == '': skills = 'None'
                heroEmbed.add_field(name='Assists', value=skills)
            if len(thisHero.skills.special) > 0:
                skills = ''
                for counter, skill in enumerate(thisHero.skills.special):
                    if skill != None:
                        skills += skill.name + ' ' + str(counter) + 'star\n'
                if skills == '': skills = 'None'
                heroEmbed.add_field(name='Specials', value=skills)
            if len(thisHero.skills.passiveA) > 0:
                skills = ''
                for counter, skill in enumerate(thisHero.skills.passiveA):
                    if skill != None:
                        skills += skill.name + ' ' + str(counter) + 'star\n'
                if skills == '': skills = 'None'
                heroEmbed.add_field(name='Passive A', value=skills)
            if len(thisHero.skills.passiveB) > 0:
                skills = ''
                for counter, skill in enumerate(thisHero.skills.passiveB):
                    if skill != None:
                        skills += skill.name + ' ' + str(counter) + 'star\n'
                if skills == '': skills = 'None'
                heroEmbed.add_field(name='Passive B', value=skills)
            if len(thisHero.skills.passiveC) > 0:
                skills = ''
                for counter, skill in enumerate(thisHero.skills.passiveC):
                    if skill != None:
                        skills += skill.name + ' ' + str(counter) + 'star\n'
                if skills == '': skills = 'None'
                heroEmbed.add_field(name='Passive C', value=skills)
            await message.channel.send(embed=heroEmbed)
            return


        if lowerMessage.startswith('test'):
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
