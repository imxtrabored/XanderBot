from discord import Embed

from command.barracks_delete import BarracksDelete
from command.barracks_list import BarracksList
from command.barracks_rename import BarracksRename
from command.barracks_save import BarracksSave
from command.cmd_default import CmdDefault
from command.devs import Devs
from command.donate import Donate
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
from command.common import ReplyPayload, filter_name
from feh.emojilib import EmojiLib as em


class HelpCmd(CmdDefault):

    TITLE_1 = 'Welcome to the Order of Heroes!'

    TITLE_2 = 'General Commands'

    TITLE_3 = 'Barracks System'

    TITLE_4 = 'Tips'

    DEFAULT_HELP_1 = (
        'I am Xander, the crown prince of Nohr. As you are the tactician for '
        'the Order of Heroes, it is imperative that you understand the allies '
        'in your midst as well as the enemies we face. Therefore, as an '
        'experienced general of the Nohrian armies, I have compiled a '
        'catalogue of the Heroes we may encounter and all of their various '
        'abilities.\n'
        'Use this wisely, summoner, for there are dark times ahead of us.\n\n'
        'The following commands are available. Use ``f?help {command name}``'
        'to get the details of any command.'
    )

    DEFAULT_HELP_2 = (
        '``hero``: Displays a summary of a hero\'s attributes and skils. Try '
        'using this command as a unit builder mock-up tool.\n'
        '``stats``: Displays a summary of a hero\'s attributes.\n'
        '``skills``: Displays a hero\'s default skills.\n'
        '``compare``: Comapres the attributes of one or more heroes.\n'
        '``alts``: Shows the available alternate forms of a hero.\n'
        '``merges``: Shows a brief summary of the bonuses gained by merging '
        'extra copies a hero.\n'
        '``totalsp``: Shows the total SP needed to learn a hero\'s skills.\n'
        '``art``: Shows the in-game artwork for a hero.\n'
        '``skill``: Shows the details of a particular skill.\n'
        '``skillsearch``: Searches for a skill based on any search terms. Use '
        '``f?help skillsearch`` for advanced syntax.\n'
        '``addalias``: Adds an alternate name for a hero to my database.\n'
        '``skillalias``: Adds an alternate name for a skill to my database.\n'
        '``ping``: Displays my current latency to Discord\'s servers.\n'
        '``devs``: Find out about XanderBot\'s development team.\n'
        '``donate``: Find out how you can make donations.'
    )

    DEFAULT_HELP_3 = (
        'Use ``f?help barracks`` for a more detailed overview of the barracks '
        'and custom hero saving feature.\n'
        '``barracks``: Lists the units in your barracks.\n'
        '``save``: Summons a custom unit into your barracks. You may find it '
        'easier to quicksave using the reactions on the ``hero`` or ``stats`` '
        'commands; see ``f?help save`` for details.\n'
        '``rename``: Renames the custom name for a hero in your barracks.\n'
        '``sendhome``: Removes a unit from your barracks.'
    )

    DEFAULT_HELP_4 = (
        'For help on attributes that can be added to heroes in a command, '
        'use ``f?help syntax``.\n'
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
    async def cmd(params, user_id):
        if params:
            embed = None
            params = filter_name(params)
            if params in COMMAND_DICT:
                content = COMMAND_DICT[params].help_text
            else:
                content = 'Sorry, that command is invalid.'
        else:
            content = None
            embed = Embed()
            embed.title = HelpCmd.TITLE_1
            embed.description = HelpCmd.DEFAULT_HELP_1
            embed.add_field(
                name=HelpCmd.TITLE_2,
                value=HelpCmd.DEFAULT_HELP_2,
                inline=True
            )
            embed.add_field(
                name=HelpCmd.TITLE_3,
                value=HelpCmd.DEFAULT_HELP_3,
                inline=True
            )
            embed.add_field(
                name=HelpCmd.TITLE_4,
                value=HelpCmd.DEFAULT_HELP_4,
                inline=True
            )
            embed.color = em.get_color(None)
        return ReplyPayload(content=content, embed=embed)


COMMAND_DICT = {
    'help'       : HelpCmd,
    'about'      : HelpCmd,
    'barracks'   : BarracksList,
    'saved'      : BarracksList,
    'savedheroes': BarracksList,
    'save'       : BarracksSave,
    'rename'     : BarracksRename,
    'delete'     : BarracksDelete,
    'sendhome'   : BarracksDelete,
    'hero'       : HeroInfo,
    'unit'       : HeroInfo,
    'stat'       : HeroStats,
    'stats'      : HeroStats,
    'skills'     : HeroSkills,
    'totalsp'    : HeroTotalSp,
    'compare'    : HeroCompare,
    'alt'        : HeroAlts,
    'alts'       : HeroAlts,
    'merge'      : HeroMerges,
    'merges'     : HeroMerges,
    'art'        : HeroArt,
    'skill'      : SkillInfo,
    'skillsearch': SkillSearch,
    'searchskills': SkillSearch,
    'searchskill': SkillSearch,
    'ssearch'    : SkillSearch,
    'list'       : HeroList,
    'herolist'   : HeroList,
    'hlist'      : HeroList,
    'listheroes' : HeroList,
    'heroes'     : HeroList,
    'herosearch' : HeroList,
    'searchhero' : HeroList,
    'searchheroes': HeroList,
    'hsearch'    : HeroList,
    'sort'       : HeroSort,
    'addalias'   : HeroAlias,
    'skillalias' : SkillAlias,
    'minesweeper': Minesweeper,
    'minesweep'  : Minesweeper,
    'mines'      : Minesweeper,
    'ping'       : Ping,
    'devs'       : Devs,
    'developers' : Devs,
    'authors'    : Devs,
    'donate'     : Donate,
    'donation'   : Donate,
    'donations'  : Donate,
    'syntax'     : Syntax,
}
