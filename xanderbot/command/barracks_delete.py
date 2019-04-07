from command.cmd_default import CmdDefault
from command.common import UserPrompt, ReplyPayload
from command.common_barracks import callback_delete
from feh.unitlib import UnitLib


class BarracksDelete(CmdDefault):
    """description of class"""

    help_text = (
        'The ``sendhome`` command removes units from your barracks.\n\n'
        'Usage: ``f?sendhome {custom name}, {additional names...}\n\n'
    )

    @staticmethod
    async def cmd(params, user_id):
        if not params:
            return ReplyPayload(
                content='No input. Please enter a saved heroe name.')
        search_names = params.split(',')
        names = UnitLib.get_custom_heroes_names(search_names, user_id)
        if names:
            if len(search_names) > len(names):
                inv_msg = (f'{len(search_names) - len(names)} of the custom '
                           'names provided are not in your barracks.\n')
            else:
                inv_msg = ''
            if len(names) == 1:
                return ReplyPayload(
                    replyable=UserPrompt(
                        content=(f'{inv_msg}Are you sure you want to delete '
                                 f'{names[0]}? This cannot be undone. (Y/N):'),
                        callback=callback_delete,
                        data=names
                    )
                )
            return ReplyPayload(
                replyable=UserPrompt(
                    content=(f'{inv_msg}Are you sure you want to delete '
                             f'{len(names)} heroes? This cannot be undone. '
                             '(Y/N):'),
                    callback=callback_delete,
                    data=names
                )
            )
        if len(search_names) == 1:
            return ReplyPayload(
                content='Could not find a saved hero with that name.')
        return ReplyPayload(
            content='Could not find any saved heroes with those names.')
