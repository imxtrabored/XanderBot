import asyncio
import re

from collections import namedtuple
from enum import Enum

import discord

from command import Command as Cmd
from feh.emojilib import EmojiLib as em
from feh.unitlib import UnitLib



BotReply = namedtuple('BotReply', 'bot_msg user_msg user cmd_type embed data task')
UserEditable = namedtuple('UserEditable', 'bot_msg user_msg cmd_type task')


class CMDType(Enum):
    ERROR        = (Cmd.do_nothing , Cmd.do_nothing      , Cmd.do_nothing   )
    HERO         = (Cmd.cmd_hero   , Cmd.finalize_hero   , Cmd.react_hero   )
    HERO_STATS   = (Cmd.cmd_stats  , Cmd.finalize_stats  , Cmd.react_stats  )
    HERO_SKILLS  = (Cmd.cmd_hskills, Cmd.finalize_hskills, Cmd.react_hskills)
    HERO_COMPARE = (Cmd.cmd_compare, Cmd.finalize_compare, Cmd.react_compare)
    HERO_ALTS    = (Cmd.cmd_alts   , Cmd.finalize_alts   , Cmd.react_alts   )
    HERO_MERGES  = (Cmd.cmd_merges , Cmd.finalize_merges , Cmd.react_merges )
    SKILL        = (Cmd.cmd_skill  , Cmd.finalize_skill  , Cmd.react_skill  )
    SORT         = (Cmd.do_nothing , Cmd.do_nothing      , Cmd.do_nothing   )
    ADDALIAS     = (Cmd.cmd_h_alias, Cmd.finalize_h_alias, Cmd.react_h_alias)
    SKILLALIAS   = (Cmd.cmd_s_alias, Cmd.finalize_s_alias, Cmd.react_s_alias)

    def __init__(self, cmd, finalize, react):
        self.cmd = cmd
        self.finalize = finalize
        self.react = react



class XanderBotClient(discord.Client):


    def __init__(self, *, loop = None, **options):
        super().__init__(loop = loop, options = options)
        file_name = '../tokens.txt'
        file = open (file_name, 'r')
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
        em.initialize(self)
        UnitLib.initialize_emojis(self)
        Cmd.devs.append(self.get_user(151913154803269633))
        Cmd.devs.append(self.get_user(196379129472352256))


    async def forget_editable(self, user_msg):
        try:
            await asyncio.sleep(900)
        except asyncio.CancelledError:
            pass
        finally:
            #print('editable deleted:')
            #print(user_msg.id)
            del self.reactable_library[user_msg.id]



    def register_editable(self, bot_msg, user_msg, cmd_type):
        task = asyncio.create_task(self.forget_reactable(user_msg))
        self.editable_library[user_msg.id] = UserEditable(
            bot_msg, user_msg, cmd_type, task)
        #print('editable registered:')
        #print(user_msg.id)



    async def forget_reactable(self, bot_msg):
        try:
            await asyncio.sleep(900)
        except asyncio.CancelledError:
            pass
        finally:
            #print('reactable deleted:')
            #print(bot_msg.id)
            del self.reactable_library[bot_msg.id]



    def register_reactable(self, bot_msg, user_msg, user, cmd_type,
                           embed, data):
        task = asyncio.create_task(self.forget_reactable(bot_msg))
        self.reactable_library[bot_msg.id] = BotReply(
            bot_msg, user_msg, user, cmd_type, embed, data, task)
        #print('reactable registered:')
        #print(bot_msg.id)



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
            predicate = split_command[1]
        else: predicate = ''
        try:
            #TODO: kind of gross line, also investigate if RE or map is faster here?
            if   lower_message.startswith('hero') or lower_message.startswith('unit'):
                command_type = CMDType.HERO
            elif lower_message.startswith('stat'):
                command_type = CMDType.HERO_STATS
            elif lower_message.startswith('skills'):
                command_type = CMDType.HERO_SKILLS
            elif lower_message.startswith('compare'):
                command_type = CMDType.HERO_COMPARE
            elif lower_message.startswith('alt'):
                command_type = CMDType.HERO_ALTS
            elif lower_message.startswith('merge'):
                command_type = CMDType.HERO_MERGES
            elif lower_message.startswith('skill '):
                command_type = CMDType.SKILL
            elif lower_message.startswith('addalias'):
                command_type = CMDType.ADDALIAS
            elif lower_message.startswith('skillalias'):
                command_type = CMDType.SKILLALIAS
            else: command_type = None

            if command_type:
                content, embed, data = await command_type.cmd(predicate)
                bot_reply = await message.channel.send(
                    content = content, embed = embed)
                self.register_editable(bot_reply, message, [command_type])
                if data:
                    self.register_reactable(bot_reply, message, message.author,
                                            command_type, embed, data)
                    await command_type.finalize(bot_reply)
                return

            #debug commands
            if lower_message.startswith('ping'):
                await message.channel.send(
                    f'Ping: {round(self.latency * 1000, 3)} ms')


            elif (lower_message.startswith('emojis')
                and (message.author.id == 151913154803269633
                     or message.author.id == 196379129472352256)):
                emojilisttemp = sorted(self.emojis, key=lambda q: (q.name))
                for e in emojilisttemp:
                    await message.channel.send(str(e) + str(e.id))

            elif (lower_message.startswith('reload')
                  and (message.author.id == 151913154803269633
                       or message.author.id == 196379129472352256)):
                reply = await message.channel.send(
                    'Rebuilding hero, skill, and emoji indices...')
                UnitLib.initialize()
                UnitLib.initialize_emojis(self)
                em.initialize(self)
                await reply.edit(content = 'Done rebuilding all indices.')

            elif (lower_message.startswith('say')
                  and (message.author.id == 151913154803269633
                       or message.author.id == 196379129472352256)):
                payload = message.content.split(' ', 2)[1:]
                await self.get_channel(int(payload[0])).send(payload[1])

            elif lower_message.startswith('whoami'):
                await message.channel.send(f"You're <{message.author.id}>!")
            else:
                bot_reply = await message.channel.send('Command invalid!')
                self.register_editable(bot_reply, message, [CMDType.ERROR])
        except Exception as e:
            bot_reply = await message.channel.send('An unknown error has occured.')
            self.register_editable(bot_reply, message, [CMDType.ERROR])
            raise e



    async def on_message_edit(self, before, after):
        if after.author == self.user:
            return
        test_string = after.content[:4].lower()
        if not (test_string.startswith('f?') or test_string.startswith('feh?')):
            return
        if after.id not in self.editable_library:
            return
        msg_bundle = self.editable_library.get(after.id)
        bot_msg = msg_bundle.bot_msg

        lower_message = after.content.lower()

        if lower_message.startswith('f?'):
            lower_message = lower_message[2:]
        elif lower_message.startswith('feh?'):
            lower_message = lower_message[4:]
        split_command = lower_message.split(' ', 1)
        if len(split_command) > 1:
            predicate = split_command[1]
        else: predicate = ''
        try:
            if   lower_message.startswith('hero') or lower_message.startswith('unit'):
                command_type = CMDType.HERO
            elif lower_message.startswith('stat'):
                command_type = CMDType.HERO_STATS
            elif lower_message.startswith('skills'):
                command_type = CMDType.HERO_SKILLS
            elif lower_message.startswith('compare'):
                command_type = CMDType.HERO_COMPARE
            elif lower_message.startswith('alt'):
                command_type = CMDType.HERO_ALTS
            elif lower_message.startswith('merge'):
                command_type = CMDType.HERO_MERGES
            elif lower_message.startswith('skill '):
                command_type = CMDType.SKILL
            elif lower_message.startswith('addalias'):
                command_type = CMDType.ADDALIAS
            elif lower_message.startswith('skillalias'):
                command_type = CMDType.SKILLALIAS
            else:
                command_type = None

            if command_type:
                content, embed, data = await command_type.cmd(predicate)
                if bot_msg.id in self.reactable_library:
                    self.reactable_library.get(bot_msg.id).task.cancel()
                await bot_msg.edit(
                    content = content, embed = embed)

                if command_type != msg_bundle.cmd_type[0]:
                    msg_bundle.cmd_type[0] = command_type
                    await bot_msg.clear_reactions()
                    if data:
                        self.register_reactable(bot_msg, after, after.author,
                                                command_type, embed, data)
                        await command_type.finalize(bot_msg)
            else:
                await bot_msg.edit(content = 'Command invalid!', embed = None)
                if msg_bundle.cmd_type[0] != CMDType.ERROR:
                    await bot_msg.clear_reactions()
                    msg_bundle.cmd_type[0] = CMDType.ERROR

        except:
            await bot_msg.edit(
                content = 'An unknown error has occured.', embed = None)
            msg_bundle.cmd_type[0] = CMDType.ERROR
            raise



    async def on_reaction_add(self, reaction, user):
        if (reaction.message.author != client.user
            or user == client.user
            or reaction.message.id not in self.reactable_library): return
        msg_bundle = self.reactable_library.get(reaction.message.id)
        if user != msg_bundle.user: return
        bot_msg = msg_bundle.bot_msg
        content, embed, remove = await msg_bundle.cmd_type.react(
            reaction, bot_msg, msg_bundle.embed, msg_bundle.data)
        manage_msg = bot_msg.channel.permissions_for(bot_msg.author).manage_messages
        if manage_msg and remove:
            asyncio.create_task(bot_msg.remove_reaction(reaction, user))

        if content is None: content = bot_msg.content
        if embed is None and bot_msg.embed:
            content = msg_bundle.bot_msg.embed[0]
        await msg_bundle.bot_msg.edit(content = content, embed = embed)



client = XanderBotClient()
client.run(client.token)
