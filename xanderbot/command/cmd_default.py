
class CmdDefault(object):

    help_text = 'No help is available for this command.'

    @staticmethod
    async def cmd(params):
        return 'No response.', None, None



    @staticmethod
    async def finalize(bot_reply):
        return



    @staticmethod
    async def react(reaction, bot_msg, embed, data):
        return None, None, False
