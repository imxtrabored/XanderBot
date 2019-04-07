from command.cmd_default import CmdDefault
from command.common import ReplyPayload


class HeroSort(CmdDefault):

    @staticmethod
    async def cmd(params, user_id):
        return ReplyPayload(content='Command not implemented yet!')

