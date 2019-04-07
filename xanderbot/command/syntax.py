from command.cmd_default import CmdDefault
from command.common import ReplyPayload


class Syntax(CmdDefault):
    """description of class"""

    help_text = (
        'When in doubt about hero names, try finding a hero using "Heroname: '
        'Epithet" format or use the ``f?alts`` command to find my preferred '
        'short name. Non-seasonal hero alts use the subtitle "(Alt 1)" by '
        'default.\n\n'
        'If a name input matches more than one hero, one hero is selected at '
        'random. You can also include the word ``random`` to find a random '
        'unit of a certain type; e.g. ``f?hero random armor mage`` or '
        '``f?hero random camilla``. This type of usage also allows similar '
        'logical operators to the ``skillsearch`` command; see ``f?help '
        'skillsearch``for more details.\n\n'
        'Attributes applicable to heroes include:\n'
        'Assets: ``+hp, +atk, +spd, +def, or +res``\n'
        'Flaws: ``-hp, -atk, -spd, -def, or -res``\n'
        'Merges: ``+#``\n'
        'Rarity: ``#*``\n'
        'Dragonflowers: ``++#``\n'
        'Summoner Support: ``support a`` or ``support 3``\n'
        'Skills: The name of the skill, or ``summoned`` to automatically add '
        'a hero\'s default equipped skills.\n\n'
        'Each of these attributes have multiple aliases for ease and clarity. '
        'For instance, ``++3``, ``df: 3``, ``3 dragonflowers``, and other '
        'variants are understood by XanderBot. Don\'t forget to delimit '
        'hero attributes by commas.'
    )

    @staticmethod
    async def cmd(params, user_id):
        return ReplyPayload(content=Syntax.help_text)
