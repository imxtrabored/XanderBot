from command.common import ReplyPayload, UserPrompt
from feh.unitlib import UnitLib


async def callback_save(custom_name, hero, user_id, *, err_text=''):
    if custom_name == 'cancel':
        return ReplyPayload(content='Canceled. Hero was not saved.')
    hero.custom_name = custom_name
    status = UnitLib.insert_custom_hero(hero, user_id)
    if status == 0:
        return ReplyPayload(content=f'{err_text}Build saved as "{custom_name}"!')
    if status == 1:
        return ReplyPayload(
            replyable=UserPrompt(
                callback=callback_save,
                content=(
                    f'{err_text}Name is invalid (matches normal hero). Enter '
                    f'a new name for custom {hero.short_name} (or "cancel"):'
                ),
                data=hero
            )
        )
    if status == 2:
        return ReplyPayload(
            content=(f'{err_text}Your barracks is full (300)! Please send '
                     'heroes home before adding new heroes. (``delete`` or '
                     '``sendhome``.)')
        )
    if status == 3:
        return ReplyPayload(
            replyable=UserPrompt(
                callback=callback_overwrite,
                content=(f'{err_text}A hero with that name or a similar name '
                         'is already in your barracks.  Overwrite it? (Y/N):'),
                data=hero
            )
        )

async def callback_overwrite(response, hero, user_id):
    if response.lower() in {'y', 'yes', 'overwrite'}:
        if UnitLib.update_custom_hero(hero, user_id):
            return ReplyPayload(content='Saved hero updated!')
        return await callback_save(hero.custom_name, hero, user_id)
    return ReplyPayload(content='Canceled. Hero was not saved.')

async def callback_delete(response, hero_names, user_id):
    if response.lower() in {'y', 'yes', 'delete'}:
        names = UnitLib.get_custom_heroes_names(hero_names, user_id)
        if names:
            UnitLib.delete_custom_heroes(hero_names, user_id)
            if len(hero_names) < len(names):
                inv_msg = (f'{len(hero_names) - len(names)} heroes were not '
                           'found. They may have already been sent home.\n')
            else:
                inv_msg = ''
            if len(names) == 1:
                return ReplyPayload(
                    content=f'{inv_msg}{names[0]} was sent home.')
            return ReplyPayload(
                content=f'{inv_msg}{len(names)} heroes were sent home.')
        return ReplyPayload(
            content=(f'Error: No heroes were found. They may have '
                     'already been sent home.')
        )
    return ReplyPayload(content='Canceled. No heroes were deleted.')
