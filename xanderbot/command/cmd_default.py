
class CmdDefault(object):

    LOGGING = False
    help_text = 'No help is available for this command.'

    @staticmethod
    async def cmd(params):
        return 'No response.', None, None



    @staticmethod
    async def finalize(bot_reply, data):
        return



    @staticmethod
    async def react(reaction, bot_msg, embed, data):
        return None, None, False
