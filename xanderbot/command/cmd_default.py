from command.common import ReplyPayload


class CmdDefault(object):

    LOGGING = False

    help_text = 'No help is available for this command.'

    @staticmethod
    async def cmd(params, user_id):
        return ReplyPayload(content='No response.')
