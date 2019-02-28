from command.cmd_default import CmdDefault
from command.common import DiscordData

class Devs(CmdDefault):
    """description of class"""

    DEV_TEXT = (
        'XanderBot is written in Python by {}#{}.\n'
        'XanderBot\'s visual design is by {}#{}.\n'
        'Feel free to contact my developers for questions, bug reports, or '
        'feature requests.\n'
        'Special thanks to {}#{} for help with new units.\n'
        'Special thanks to the moderators of The Sleepy Tiki discord for '
        'advice.'
    )

    help_text = (
        'The ``devs`` command lists my development team.\n\n'
        'Usage: ``f?devs``'
    )


    @staticmethod
    async def cmd(params):
        return (
            Devs.DEV_TEXT.format(
                DiscordData.devs[0].name,
                DiscordData.devs[0].discriminator,
                DiscordData.devs[1].name,
                DiscordData.devs[1].discriminator,
                DiscordData.devs[2].name,
                DiscordData.devs[2].discriminator,
            ),
            None, None
        )
