from command.cmd_default import CmdDefault
from command.devs import Devs
from command.donate import Donate
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

from command.common import filter_name

class HelpCmd(CmdDefault):

    COMMAND_DICT = {
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
        'heroalias' : HeroAlias  ,
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

    DEFAULT_HELP = (
        'I am Xander, the crown prince of Nohr. As the tatician for the Order '
        'of Heroes, it is imperative that you understand the allies in your '
        'midst as well as the enemies we face. Therefore, as an experienced '
        'general of the Nohrian armies, I have compiled a catalogue for you '
        'of the Heroes we may encounter and all of their various abilities.\n'
        'Use this wisely, summoner, for there are dark times ahead of us.\n\n'
        'The following commands are available. Use ``f?help {command name}``'
        'to get details of any command.\n'
        '``stats``: Displays a summary of a hero\'s attributes.\n'
        '``skills``: Displays a hero\'s default skills.\n'
        '``compare``: Comapres the attributes of one or more heroes.\n'
        '``alts``: Shows the available alternate forms of a hero.\n'
        '``merges``: Shows a brief summary of the bonuses gained by merging '
        'extra copies a hero.\n'
        '``art``: Shows the in-game artwork for a hero.\n'
        '``skill``: Shows the details of a particular skill.\n'
        '``addalias``: Adds an alternate name for a hero to my database.\n'
        '``skillalias``: Adds an alternate name for a skill to my database.\n'
        '``ping``: Displays my current latency to the Discord server.\n'
        '``devs``: Find out about XanderBot\'s development team.\n'
        '``donate``: Find out how you can make donations.\n'
        'For help on attributes that can be added to heroes in a command, '
        'use ``f?help syntax``.\n\n'
        'Tips:\n'
        'Several commands have additional aliases to improve usability.\n'
        'Use the reaction emojis to modify the output of commands.\n'
        'Alternatively, editing your message will cause me to edit my reply '
        'accordingly, even if the entire command is different.\n'
        'You can contact my developers for requests, suggestions, or bugs.'
    )

    help_text = (
        'The ``help`` command displays extra information about my '
        'functionality and commands.\n\n'
        'Usage: ``f?help | {optional command name}``\n\n'
        'If a command name is specified, then details about the command are '
        'shown. Otherwise, the ``help`` command summarizes available commands.'
    )

    @staticmethod
    async def cmd(params):
        if params:
            params = filter_name(params)
            if params in HelpCmd.COMMAND_DICT:
                content = HelpCmd.COMMAND_DICT[params].help_text
            else:
                content = 'Sorry, that command is invalid.'
        else:
            content = HelpCmd.DEFAULT_HELP

        return content, None, None

HelpCmd.COMMAND_DICT['help'] = HelpCmd
HelpCmd.COMMAND_DICT['about'] = HelpCmd
