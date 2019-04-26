from command.cmd_default import CmdDefault
from command.common import DiscordData, ReplyPayload


class Devs(CmdDefault):
    """description of class"""

    DEV_TEXT = (
        'XanderBot is written in Python by {}\n'
        'XanderBot\'s visual design is by {}.\n'
        'Special thanks to {} for massive contributions to XanderBot '
        'data.\n'
        'Feel free to contact my developers for questions, bug reports, or '
        'feature requests.\n'
        'Special thanks to the moderators of The Sleepy Tiki discord for '
        'advice.'
    )

    help_text = (
        'The ``devs`` command lists the members of my development team.\n\n'
        'Usage: ``f?devs``'
    )

    @staticmethod
    async def cmd(params, user_id):
        return ReplyPayload(
            content=Devs.DEV_TEXT.format(
                str(DiscordData.devs[0]),
                str(DiscordData.devs[1]),
                str(DiscordData.devs[2]),
            )
        )
