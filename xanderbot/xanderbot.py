import asyncio

from collections import namedtuple
from enum import Enum

import discord
from command.common import DiscordData
from command.cmd_default import CmdDefault
from command.devs import Devs
from command.donate import Donate
from command.help import HelpCmd
from command.hero_info import HeroInfo
from command.hero_alias import HeroAlias
from command.hero_alts import HeroAlts
from command.hero_art import HeroArt
from command.hero_compare import HeroCompare
from command.hero_merges import HeroMerges
from command.hero_skills import HeroSkills
from command.hero_sort import HeroSort
from command.hero_stats import HeroStats
from command.ping import Ping
from command.skill_info import SkillInfo
from command.skill_alias import SkillAlias
from command.syntax import Syntax

from feh.emojilib import EmojiLib as em
from feh.unitlib import UnitLib
try:
    import easter_egg
except ImportError:
    easter_eggs = False
else:
    easter_eggs = True



BotReply = namedtuple('BotReply', 'bot_msg user_msg user cmd_type embed data task')
UserEditable = namedtuple('UserEditable', 'bot_msg user_msg task')

"""
class CMDType(Enum):
    ERROR        = CmdDefault
    HERO         = HeroInfo
    HERO_STATS   = HeroStats
    HERO_SKILLS  = HeroSkills
    HERO_COMPARE = HeroCompare
    HERO_ALTS    = HeroAlts
    HERO_MERGES  = HeroMerges
    HERO_ART     = HeroArt
    SKILL        = SkillInfo
    SORT         = HeroSort
    ADDALIAS     = HeroAlias
    SKILLALIAS   = SkillAlias

    def __init__(self, module):
        self.cmd = module.cmd
        self.finalize = module.finalize
        self.react = module.react

COMMAND_DICT = {
    'hero'      : CMDType.HERO        ,
    'unit'      : CMDType.HERO        ,
    'stat'      : CMDType.HERO_STATS  ,
    'stats'     : CMDType.HERO_STATS  ,
    'skills'    : CMDType.HERO_SKILLS ,
    'compare'   : CMDType.HERO_COMPARE,
    'alt'       : CMDType.HERO_ALTS   ,
    'alts'      : CMDType.HERO_ALTS   ,
    'merge'     : CMDType.HERO_MERGES ,
    'merges'    : CMDType.HERO_MERGES ,
    'art'       : CMDType.HERO_ART    ,
    'skill'     : CMDType.SKILL       ,
    'sort'      : CMDType.SORT        ,
    'addalias'  : CMDType.ADDALIAS    ,
    'skillalias': CMDType.SKILLALIAS  ,
}
"""

COMMAND_DICT = {
    'help'      : HelpCmd    ,
    'about'     : HelpCmd    ,
    'hero'      : HeroInfo   ,
    'unit'      : HeroInfo   ,
    'stat'      : HeroStats  ,
    'stats'     : HeroStats  ,
    'skills'    : HeroSkills ,
    'compare'   : HeroCompare,
    'alt'       : HeroAlts   ,
    'alts'      : HeroAlts   ,
    'merge'     : HeroMerges ,
    'merges'    : HeroMerges ,
    'art'       : HeroArt    ,
    'skill'     : SkillInfo  ,
    'sort'      : HeroSort   ,
    'addalias'  : HeroAlias  ,
    'skillalias': SkillAlias ,
    'ping'      : Ping       ,
    'devs'      : Devs       ,
    'developers': Devs       ,
    'authors'   : Devs       ,
    'donate'    : Donate     ,
    'donation'  : Donate     ,
    'donations' : Donate     ,
    'syntax'    : Syntax     ,
}


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
        DiscordData.setup_commands(self)
        #if not Cmd.devs:
        #    Cmd.devs.append(self.get_user(151913154803269633))
        #    Cmd.devs.append(self.get_user(196379129472352256))


    async def forget_editable(self, user_msg):
        try:
            await asyncio.sleep(900)
        except asyncio.CancelledError:
            pass
        finally:
            #print('editable deleted:')
            #print(user_msg.id)
            del self.reactable_library[user_msg.id]



    def register_editable(self, bot_msg, user_msg):
        task = asyncio.create_task(self.forget_reactable(user_msg))
        self.editable_library[user_msg.id] = UserEditable(
            bot_msg, user_msg, task)
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
        if easter_egg:
            asyncio.create_task(easter_egg.process_eggs(self, message))
        test_string = message.content[:4].lower()
        if not (test_string.startswith('f?') or test_string.startswith('feh?')):
            return
        asyncio.create_task(message.channel.trigger_typing())
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
            if split_command[0] in COMMAND_DICT:
                command_type = COMMAND_DICT[split_command[0]]
                content, embed, data = await command_type.cmd(predicate)
                bot_reply = await message.channel.send(
                    content = content, embed = embed)
                self.register_editable(bot_reply, message)
                if data:
                    self.register_reactable(bot_reply, message, message.author,
                                            command_type, embed, data)
                    await command_type.finalize(bot_reply)
                if command_type == HeroAlias or command_type == SkillAlias:
                    await DiscordData.devs[0].send(
                        content = f'{message.author} addded alias')
                return

            #debug commands

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
                self.register_editable(bot_reply, message)

        except discord.HTTPException as e:
            bot_reply = await message.channel.send(
                'Discord connection or server issue. Please try again later.'
            )
            self.register_editable(bot_reply, message)
            raise e

        except Exception as e:
            bot_reply = await message.channel.send(
                'An unknown error has occured. This should never happen; '
                'please report this to a developer.'
            )
            self.register_editable(bot_reply, message)
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
        manage_messages = bot_msg.channel.permissions_for(bot_msg.author).manage_messages

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
            command_type = COMMAND_DICT.get(split_command[0])

            if command_type:
                content, embed, data = await command_type.cmd(predicate)
                await bot_msg.edit(
                    content = content, embed = embed)
                if bot_msg.id in self.reactable_library:
                    self.reactable_library.get(bot_msg.id).task.cancel()
                elif data:
                    if manage_messages: await bot_msg.clear_reactions()
                    self.register_reactable(bot_msg, after, after.author,
                                            command_type, embed, data)
                    await command_type.finalize(bot_msg)
            else:
                await bot_msg.edit(content = 'Command invalid!', embed = None)
                if manage_messages: await bot_msg.clear_reactions()

        except discord.HTTPException as e:
            await bot_msg.edit(
                content = (
                    'Discord connection or server issue. Please try again '
                    'later.'
                ),
                embed = None
            )
            raise e

        except Exception as e:
            await bot_msg.edit(
                content = (
                    'An unknown error has occured. This should never happen; '
                    'please report this to a developer.'
                ),
                embed = None
            )
            raise e



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



    async def on_message_delete(self, message):
        if message.author == self.user or message.id not in self.editable_library:
            return
        msg_bundle = self.editable_library[message.id]
        if msg_bundle.bot_msg in self.reactable_library:
            self.reactable_library[bot_msg.id].task.cancel()
        await msg_bundle.bot_msg.delete()
        msg_bundle.task.cancel()




client = XanderBotClient()
client.run(client.token)
