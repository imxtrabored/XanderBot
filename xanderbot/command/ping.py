from command.common import DiscordData
from command.cmd_default import CmdDefault

class Ping(CmdDefault):

    help_text = (
        'The ``ping`` command displays my current latency to Discord.\n\n'
        'Usage: ``f?ping``'
    )

    @staticmethod
    async def cmd(params):
        return (
            f'Pong: {round(DiscordData.client.latency * 1000, 3)} ms',
            None, None
        )


    @staticmethod
    async def finalize(bot_reply):
        return


    @staticmethod
    async def react(reaction, bot_msg, embed, data):
        return
