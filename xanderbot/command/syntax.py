from command.cmd_default import CmdDefault

class Syntax(CmdDefault):
    """description of class"""

    help_text = (
        'When in doubt about hero names, try finding a hero using "Heroname: '
        'Epithet" format or use the ``f?alts`` command to find my preferred '
        'short name. Non-seasonal hero alts use the subtitle "(Alt 1)" by '
        'default.\n\n'
        'Attributes applicable to heroes include:\n'
        'Assets: ``+hp, +atk, +spd, +def, +res``\n'
        'Flaws: ``-hp, -atk, -spd, -def, -res``\n'
        'Merges: ``+#``\n'
        'Rarity: ``#*``\n'
        'Dragonflowers: ``++#``\n\n'
        'Each of these attributes have multiple aliases for ease and clarity. '
        'For instance, ``++3``, ``df: 3``, ``3 dragonflowers``, and many other '
        'variants are understood by XanderBot. Don\'t forget to delimit '
        'hero attributes by commas.'
    )

    @staticmethod
    async def cmd(params):
        return help_text, None, None
