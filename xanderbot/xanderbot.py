import asyncio
from collections import namedtuple
from enum import Enum
from string import punctuation

import discord

from command.barracks_delete import BarracksDelete
from command.barracks_list import BarracksList
from command.barracks_rename import BarracksRename
from command.barracks_save import BarracksSave
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
from command.hero_list import HeroList
from command.hero_merges import HeroMerges
from command.hero_skills import HeroSkills
from command.hero_sort import HeroSort
from command.hero_stats import HeroStats
from command.hero_total_sp import HeroTotalSp
from command.minesweeper import Minesweeper
from command.ping import Ping
from command.skill_info import SkillInfo
from command.skill_search import SkillSearch
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

REMOVE_PUNCT = str.maketrans('', '', punctuation)

Reactable = namedtuple(
    'Reactable', 'bot_msg callback user data self_destruct task')
Editable = namedtuple(
    'Editable', 'bot_msg user_msg cmd_type task')
Replyable = namedtuple(
    'Replyable', 'bot_msg channel_id callback fallback data task')

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
    'help'       : HelpCmd       ,
    'about'      : HelpCmd       ,
    'barracks'   : BarracksList  ,
    'saved'      : BarracksList  ,
    'savedheroes': BarracksList  ,
    'save'       : BarracksSave  ,
    'rename'     : BarracksRename,
    'delete'     : BarracksDelete,
    'sendhome'   : BarracksDelete,
    'hero'       : HeroInfo      ,
    'unit'       : HeroInfo      ,
    'stat'       : HeroStats     ,
    'stats'      : HeroStats     ,
    'skills'     : HeroSkills    ,
    'totalsp'    : HeroTotalSp   ,
    'compare'    : HeroCompare   ,
    'alt'        : HeroAlts      ,
    'alts'       : HeroAlts      ,
    'merge'      : HeroMerges    ,
    'merges'     : HeroMerges    ,
    'art'        : HeroArt       ,
    'skill'      : SkillInfo     ,
    'seal'       : SkillInfo     ,
    'skillsearch': SkillSearch   ,
    'searchskills': SkillSearch  ,
    'searchskill': SkillSearch   ,
    'ssearch'    : SkillSearch   ,
    'list'       : HeroList      ,
    'herolist'   : HeroList      ,
    'hlist'      : HeroList      ,
    'listheroes' : HeroList      ,
    'heroes'     : HeroList      ,
    'herosearch' : HeroList      ,
    'searchhero' : HeroList      ,
    'searchheroes': HeroList     ,
    'hsearch'    : HeroList      ,
    'sort'       : HeroSort      ,
    'addalias'   : HeroAlias     ,
    'skillalias' : SkillAlias    ,
    'minesweeper': Minesweeper   ,
    'minesweep'  : Minesweeper   ,
    'mines'      : Minesweeper   ,
    'ping'       : Ping          ,
    'devs'       : Devs          ,
    'developers' : Devs          ,
    'authors'    : Devs          ,
    'donate'     : Donate        ,
    'donation'   : Donate        ,
    'donations'  : Donate        ,
    'syntax'     : Syntax        ,
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
        self.replyable_library = dict()
        #optimization
        self.reply_listen = False

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        em.initialize(self)
        UnitLib.initialize_emojis(self)
        await DiscordData.setup_commands(self)
        #if not Cmd.devs:
        #    Cmd.devs.append(self.get_user(151913154803269633))
        #    Cmd.devs.append(self.get_user(196379129472352256))

    async def forget_editable(self, user_msg):
        try:
            await asyncio.sleep(900)
        except asyncio.CancelledError:
            pass
        finally:
            del self.editable_library[user_msg.id]

    def register_editable(self, bot_msg, user_msg, cmd_type):
        task = asyncio.create_task(self.forget_reactable(user_msg))
        self.editable_library[user_msg.id] = Editable(
            bot_msg, user_msg, [cmd_type], task)

    async def forget_reactable(self, bot_msg):
        try:
            await asyncio.sleep(900)
        except asyncio.CancelledError:
            pass
        finally:
            del self.reactable_library[bot_msg.id]

    def register_reactable(self, bot_msg, callback, user, data, self_destruct):
        task = asyncio.create_task(self.forget_reactable(bot_msg))
        self.reactable_library[bot_msg.id] = Reactable(
            bot_msg, callback, user, data, self_destruct, task)

    async def forget_replyable(self, user_id):
        try:
            await asyncio.sleep(900)
        except asyncio.CancelledError:
            pass
        else:
            # could maybe reply here, but this is currently unused anyways
            if self.replyable_library[user_id].fallback:
                payload = self.replyable_library[user_id].fallback(
                    self.replyable_library[user_id].data, user_id)
        finally:
            del self.replyable_library[user_id]
            if not self.replyable_library:
                self.reply_listen = False

    async def handle_replyable(self, replyable, user, channel):
        if replyable.content or replyable.embed:
            bot_msg = await channel.send(
                content = replyable.content, embed = replyable.embed)
        else:
            bot_msg = None
        task = asyncio.create_task(self.forget_replyable(user.id))
        if (user.id in self.replyable_library
                and self.replyable_library[user.id].channel_id == channel.id):
            if self.replyable_library[user.id].bot_msg:
                await self.replyable_library[user.id].bot_msg.delete()
            self.replyable_library[user.id].task.cancel()
            await self.replyable_library[user.id].task
        self.replyable_library[user.id] = Replyable(
            bot_msg, channel.id, replyable.callback, replyable.fallback,
            replyable.data, task
        )
        self.reply_listen = True

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        if easter_egg:
            asyncio.create_task(easter_egg.process_eggs(self, message))
        test_string = message.content[:4].lower()
        if not (
                test_string.startswith('f?')
                or test_string.startswith('feh?')
            ):
            if (self.reply_listen
                    and message.author.id in self.replyable_library
                    and (message.channel.id ==
                         self.replyable_library[message.author.id].channel_id)
                ):
                replyable = self.replyable_library[message.author.id]
                payload = await replyable.callback(
                    message.content, replyable.data, message.author.id)
                if payload.content or payload.embed:
                    if replyable.bot_msg:
                        bot_msg = replyable.bot_msg
                        await replyable.bot_msg.edit(
                            content = payload.content, embed = payload.embed)
                    else:
                        bot_msg = await message.channel.send(
                            content = payload.content, embed = payload.embed)
                replyable.task.cancel()
                await replyable.task
                if payload.replyable:
                    await self.handle_replyable(
                        payload.replyable, message.author, message.channel)
                if payload.reactable:
                    self.register_reactable(
                        bot_msg,
                        payload.reactable.callback,
                        message.author,
                        payload.reactable.data,
                        payload.reactable.self_destruct,
                    )
                    for emoji in payload.reactable.emojis:
                        await bot_msg.add_reaction(emoji)
                return
            else:
                return
        # asyncio.create_task(message.channel.trigger_typing())
        if test_string.startswith('feh'):
            content = message.content[4:]
        else:
            content = message.content[2:]
        split_command = content.split(' ', 1)
        if len(split_command) > 1:
            predicate = split_command[1]
        else: predicate = ''
        try:
            command = split_command[0].lower().translate(REMOVE_PUNCT)
            if command in COMMAND_DICT:
                command_type = COMMAND_DICT[command]
                payload = await command_type.cmd(predicate, message.author.id)
                if payload.content or payload.embed:
                    bot_reply = await message.channel.send(
                        content=payload.content, embed=payload.embed)
                    self.register_editable(bot_reply, message, command_type)
                else:
                    bot_reply = None
                if payload.replyable:
                    await self.handle_replyable(
                        payload.replyable, message.author, message.channel)
                if payload.reactable and bot_reply is not None:
                    self.register_reactable(
                        bot_reply,
                        payload.reactable.callback,
                        message.author,
                        payload.reactable.data,
                        payload.reactable.self_destruct,
                    )
                    for emoji in payload.reactable.emojis:
                        await bot_reply.add_reaction(emoji)
                if command_type.LOGGING:
                    await DiscordData.devs[0].send(
                        content = f'{message.author}: {message.content}')
                return
            #debug commands
            elif (split_command[0].lower() == 'emojis'
                and (message.author.id == 151913154803269633
                        or message.author.id == 196379129472352256)):
                emojilisttemp = sorted(self.emojis, key=lambda q: (q.name))
                for e in emojilisttemp:
                    await message.channel.send(str(e) + str(e.id))

            elif (split_command[0].lower().startswith('reload')
                    and (message.author.id == 151913154803269633
                        or message.author.id == 196379129472352256)):
                reply = await message.channel.send(
                    'Rebuilding hero, skill, and emoji indices...')
                UnitLib.initialize()
                UnitLib.initialize_emojis(self)
                em.initialize(self)
                await reply.edit(content = 'Done rebuilding all indices.')

            elif (split_command[0].lower() == 'say'
                  and (message.author.id == 151913154803269633
                       or message.author.id == 196379129472352256)):
                payload = message.content.split(' ', 2)[1:]
                await self.get_channel(int(payload[0])).send(payload[1])

            elif split_command[0].lower() == 'whoami':
                await message.channel.send(f"You're <{message.author.id}>!")
            else:
                bot_reply = await message.channel.send('Command invalid!')
                self.register_editable(bot_reply, message, CmdDefault)

        except discord.HTTPException as e:
            bot_reply = await message.channel.send(
                'HTTP Error. This may be an issue with the Discord servers '
                'or connection, or may be an issue with my response. Please '
                'try again later.'
            )
            self.register_editable(bot_reply, message, CmdDefault)
            raise e

        except Exception as e:
            bot_reply = await message.channel.send(
                'An unknown error has occured. This should never happen; '
                'please report this to a developer.'
            )
            self.register_editable(bot_reply, message, CmdDefault)
            raise e

    async def on_message_edit(self, before, after):
        if after.author == self.user:
            return
        test_string = after.content[:4].lower()
        if not (
                test_string.startswith('f?')
                or test_string.startswith('feh?')
            ):
            return
        if after.id not in self.editable_library:
            return
        msg_bundle = self.editable_library[after.id]
        bot_msg = msg_bundle.bot_msg
        manage_messages = (bot_msg.channel.permissions_for(bot_msg.author)
                           .manage_messages)
        if test_string.startswith('feh'):
            content = after.content[4:]
        else:
            content = after.content[2:]
        split_command = content.split(' ', 1)
        if len(split_command) > 1:
            predicate = split_command[1]
        else: predicate = ''
        try:
            command = split_command[0].lower().translate(REMOVE_PUNCT)
            if command in COMMAND_DICT:
                command_type = COMMAND_DICT[command]
                payload = await command_type.cmd(predicate, after.author.id)
                await bot_msg.edit(
                    content = payload.content, embed = payload.embed)
                if bot_msg.id in self.reactable_library:
                    self.reactable_library[bot_msg.id].task.cancel()
                    await self.reactable_library[bot_msg.id].task
                if payload.replyable:
                    await self.handle_replyable(
                        payload.replyable, after.author, after.channel)
                if payload.reactable:
                    self.register_reactable(
                        bot_msg,
                        payload.reactable.callback,
                        after.author,
                        payload.reactable.data,
                        payload.reactable.self_destruct,
                    )
                    if msg_bundle.cmd_type[0] != command_type:
                        msg_bundle.cmd_type[0] = command_type
                        if manage_messages:
                            await bot_msg.clear_reactions()
                        for emoji in payload.reactable.emojis:
                            await bot_msg.add_reaction(emoji)
                if command_type.LOGGING:
                    await DiscordData.devs[0].send(
                        content = f'{after.author}: {after.content}')
            else:
                await bot_msg.edit(content='Command invalid!', embed=None)
                if manage_messages: await bot_msg.clear_reactions()

        except discord.HTTPException as e:
            await bot_msg.edit(
                content = (
                    'HTTP Error. This may be an issue with the Discord '
                    'servers or connection, or may be an issue with my '
                    'response. Please try again later.'
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
                or reaction.message.id not in self.reactable_library):
            return
        msg_bundle = self.reactable_library[reaction.message.id]
        if user != msg_bundle.user: return
        bot_msg = msg_bundle.bot_msg
        payload = await msg_bundle.callback(
            reaction, msg_bundle.data, user.id)
        manage_msg = (bot_msg.channel.permissions_for(bot_msg.author)
                      .manage_messages)
        if manage_msg and payload.delete:
            asyncio.create_task(bot_msg.remove_reaction(reaction, user))
        if payload.replyable:
            await self.handle_replyable(
                payload.replyable, user, reaction.message.channel)
        if payload.content or payload.embed:
            content = payload.content or bot_msg.content
            if payload.embed is None and bot_msg.embeds:
                embed = msg_bundle.bot_msg.embeds[0]
            else: embed = payload.embed
            await msg_bundle.bot_msg.edit(content=content, embed=embed)
        if payload.self_destruct:
            payload.task.cancel()

    async def on_message_delete(self, message):
        if (message.author == self.user
                or message.id not in self.editable_library):
            return
        msg_bundle = self.editable_library[message.id]
        if msg_bundle.bot_msg in self.reactable_library:
            self.reactable_library[bot_msg.id].task.cancel()
        await msg_bundle.bot_msg.delete()
        msg_bundle.task.cancel()


client = XanderBotClient()
client.run(client.token)
