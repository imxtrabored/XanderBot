import discord
import asyncio

from FEH.Hero import Hero, Color, WeaponType, MoveType
from FEH.Hero import LegendElement, LegendBoost

FILENAME = "../tokens.txt"
file = open (FILENAME, "r")
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
            heroEmbed = discord.Embed(title='null')
            heroEmbed.description = 'description'
            heroEmbed.colour = discord.Colour.from_rgb(255, 0, 0)
            heroEmbed.set_footer(text='footertext')
            heroEmbed.add_field(name='field1', value='data1')
            heroEmbed.add_field(name='field2', value='data2')
            heroEmbed.add_field(name='field3', value='data3')
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