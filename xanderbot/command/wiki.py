from urllib.parse import quote_plus

from command.cmd_default import CmdDefault
from command.common import ReplyPayload


class Wiki(CmdDefault):

    help_text = 'No help is available for this command.'

    @staticmethod
    async def cmd(params, user_id):
        return ReplyPayload(content=(
            '<https://feheroes.gamepedia.com/index.php?search='
            f'{quote_plus(params)}>'
        ))
