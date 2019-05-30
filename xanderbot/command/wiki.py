from urllib.parse import quote_plus

from command.cmd_default import CmdDefault
from command.common import ReplyPayload


class Wiki(CmdDefault):

    help_text = (
        'The ``wiki`` command (alias ``w``) searches the Fire Emblem Heroes '
        'Gamepedia Wiki and returns a webpage with the results.\n\n'
        'Usage: ``f?wiki {search terms}``'
    )

    @staticmethod
    async def cmd(params, user_id):
        if not params:
            return ReplyPayload(
                content='<https://feheroes.gamepedia.com/index.php>')
        return ReplyPayload(content=(
            '<https://feheroes.gamepedia.com/index.php?search='
            f'{quote_plus(params)}>'
        ))
