from command.cmd_default import CmdDefault
from command.common import ReplyPayload
from feh.unitlib import UnitLib

class BarracksRename(CmdDefault):
    """description of class"""

    help_text = (
        'The ``rename`` command renames units from your barracks.\n\n'
        'Usage: ``f?rename {old name}, {new name}\n\n'
    )

    @staticmethod
    async def cmd(params, user_id):
        partitions = params.partition(',')
        tokens = (partitions[0].strip(), partitions[2].strip())
        if not tokens[1]:
            return ReplyPayload(
                content=('Please enter the old name followed by the new name, '
                         'separated by a comma (,).')
            )
        status, old_name = UnitLib.rename_custom_hero(
            tokens[0], tokens[1], user_id)
        if status == 1:
            return ReplyPayload(
                content=(f'Error: {tokens[1]} is too similar to the '
                         'name of an existing hero.')
            )
        if status == 2:
            return ReplyPayload(
                content=(f'Error: {tokens[0]} was not found in your '
                         'barracks.')
            )
        if status == 3:
            return ReplyPayload(
                content=(f'Error: {tokens[1]} is too similar to the '
                         'name of another hero in your barracks.')
            )
        return ReplyPayload(
            content=f'{old_name} was renamed to {tokens[1]}.'
        )
