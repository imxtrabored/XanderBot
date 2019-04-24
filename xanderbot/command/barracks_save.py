from command.cmd_default import CmdDefault
from command.common import (
    UserPrompt, ReplyPayload, SPLITTER, process_hero_args, process_hero_spaces)
from command.common_barracks import callback_save
from feh.unitlib import UnitLib

class BarracksSave(CmdDefault):
    """description of class"""

    help_text = (
        'The ``save`` command summons a custom hero into your barracks.\n\n'
        'Usage: ``f?save {new custom name}, {hero name}, {modifier 1}, '
        '{modifier 2}, {additional modifiers...}``\n\n'
        'Heroes can also be saved by reacting with 💾 on the ``hero`` or '
        '``stats`` commands. This can be much quicker, as if those commands '
        'are called using an existing custom hero, they allow you to '
        'visualize what a hero looks like before saving. Additionally, when '
        'those units call an existing custom hero, they will not prompt you '
        'for another new custom name.\n\n'
        'To modify a custom hero, you can simply use ``f?hero {custom name}, '
        '{new attribute(s)}`` and/or use the other reaction emojis before '
        'reacting with 💾 again. For instance, if you wanted to equip "My '
        'Hero" with Fury 3, and also wanted to set their merge level to '
        '4, you can simply enter ``f?hero my hero, fury, +4`` and then react '
        'with 💾. If you recently merged a copy of your hero in-game and you '
        'wanted your barracks to reflect that, you can simply use ``f?hero '
        'my hero``, react with ➕ to increase merges, then react with 💾 to '
        'save. Alternatively, you can use the ``f?save`` command to '
        'overwrite your saved hero name.'
    )

    @staticmethod
    async def cmd(params, user_id):
        if not params:
            return ReplyPayload(
                content=('No input. Please enter a new name followed by '
                         'a hero expression, separated by comma (,).')
            )
        tokens = SPLITTER.split(params)
        if len(tokens) < 2:
            #did not use commas
            tokens = params.split(' ')
            if len(tokens) < 2:
                hero = UnitLib.get_base_hero(tokens[0], user_id)
                if hero:
                    return ReplyPayload(
                        replyable=UserPrompt(
                            callback=callback_save,
                            content=(
                                f'Enter a new name for custom {hero.name}:'
                            ),
                            data=hero
                        )
                    )
                return ReplyPayload(content=(
                    'Invalid input. Please enter a new name followed by '
                    'a hero expression, separated by comma (,).'
                ))
        hero = UnitLib.get_hero(tokens[1], user_id)
        if not hero:
            hero = UnitLib.get_base_hero(tokens[0], user_id)
            if hero:
                hero, bad_args, not_allowed = process_hero_args(hero, tokens[1:])
                prepend = []
                if any(bad_args):
                    prepend.append(
                        'I did not understand the following, so they '
                        f'will not be applied: {", ".join(bad_args)}.\n\n'
                    )
                if any(not_allowed):
                    prepend.append(
                        'The following are unavailable for this hero: '
                        f'{", ".join(not_allowed)}'
                    )
                return ReplyPayload(
                    replyable=UserPrompt(
                        callback=callback_save,
                        content=(
                            f'{prepend}Enter a new name for this hero:'),
                        data=hero
                    )
                )
            hero_expr = ', '.join(tokens[1:])
            if ',' not in hero_expr:
                hero, bad_args = process_hero_spaces(hero_expr, user_id)
            if not hero:
                return ReplyPayload(
                    content=(
                        f'Hero not found: {tokens[1]}. Please enter a new '
                        'name followed by a hero expression, separated by '
                        'comma (,).'
                    ),
                )
        else:
            hero, bad_args, not_allowed = process_hero_args(hero, tokens[2:])
            new_name = tokens[0]
        return await callback_save(new_name, hero, user_id)
