from command.common import DiscordData, ReplyPayload
from command.cmd_default import CmdDefault

class Ping(CmdDefault):

    help_text = (
        'The ``ping`` command displays my current latency to Discord.\n\n'
        'Usage: ``f?ping``'
    )

    @staticmethod
    async def cmd(params, user_id):
        return ReplyPayload(
            content=f'Pong: {round(DiscordData.client.latency * 1000, 3)} ms',
        )
