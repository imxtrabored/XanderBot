from command.cmd_default import CmdDefault

class HeroSort(CmdDefault):

    @staticmethod
    async def cmd(params):
        return None, None, None


    @staticmethod
    async def finalize(bot_reply):
        return


    @staticmethod
    async def react(reaction, bot_msg, embed, data):
        return None, None, False
