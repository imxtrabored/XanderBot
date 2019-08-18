from asyncio import create_task

from command.cmd_default import CmdDefault, ReplyPayload
from command.common import DiscordData, filter_name
from feh.unitlib import UnitLib


class HeroAlias(CmdDefault):

    LOGGING = True

    help_text = (
        'The ``addalias`` command adds alternate hero name aliases to my '
        'database for more convenient searching. To add aliases for skill '
        'names, see the ``skillalias`` command instead.\n\n'
        'Usage:\n'
        'Normal Mode:``f?addalias {name 1}, {name 2}``\n'
        'Bulk Mode: ``f?addalias {existing name}, {new name 1}, {new name 2}, '
        '{additional names...}\n\n'
        'In normal mode, so long as one of the two provided names is currently '
        'valid and the other is not in my database, the invalid name will be '
        'added as an alias for the valid hero.\n'
        'In bulk mode, the first name provided must be valid. The command will '
        'try each new name against the database and add each one that does not '
        'exist to the database.\n\n'
        'Guidelines: Avoid adding meme names or foreign language names, as '
        'those could be confusing to other users. However, any name that is '
        'widely used amongst the English-speaking fanbase is acceptable even '
        'if it violates those guidelines\n'
        'Examples of acceptable names: Hinoka (Wings), A!Tiki Summer, '
        'Swordhardt, Grima, BIke, L!Tiki, Nino (Fangs), Nino (Flying)\n'
        'Examples of names to avoid: Reflet, Benchlord, Kektor, Fury Master'
    )

    @staticmethod
    async def cmd(params, user_id):
        tokens = params.split(',')
        names = [filter_name(n) for n in tokens]
        if len(names) < 2:
            return ReplyPayload(
                content='Not enough names entered. '
                'Please enter at least two names, separated by commas.'
            )
        heroes = [UnitLib.get_base_hero(n) for n in names]
        if len(names) == 2:
            if heroes[0] and not heroes[1]:
                await UnitLib.insert_hero_alias(heroes[0], names[1])
                content = (f'Added alias {tokens[1].strip()} for '
                           f'{heroes[0].short_name}.')
                create_task(DiscordData.devs[0].send(
                    #f'{message.author.name}#{message.author.discriminator} '
                    f'added alias {names[1]} for {heroes[0].short_name}.'
                ))
            elif heroes[1] and not heroes[0]:
                await UnitLib.insert_hero_alias(heroes[1], names[0])
                content = (f'Added alias {tokens[0].strip()} for '
                           f'{heroes[1].short_name}.')
                create_task(DiscordData.devs[0].send(
                    #f'{message.author.name}#{message.author.discriminator} '
                    f'added alias {names[0]} for {heroes[1].short_name}.'
                ))
            elif heroes[0] and heroes[1]:
                content = 'All names are already hero aliases!'
            else:
                content = 'Cannot find a valid hero name; need at least one.'
        elif len(names) > 2:
            if not heroes[0]:
                content = f'{tokens[0]} is not a valid hero.'
            else:
                added_names = [
                    name for name in names[1:]
                    if await UnitLib.insert_hero_alias(heroes[0], name)
                ]
                if added_names:
                    name_list = ', '.join(added_names)
                    content = (
                        f'Added aliases for {heroes[0].short_name}:\n'
                        f'{name_list}'
                    )
                    create_task(DiscordData.devs[0].send(
                        f'added aliases for {heroes[0].short_name}:\n'
                        f'{name_list}'
                    ))
                else:
                    content = 'All names are already aliases.'
        return ReplyPayload(content=content)
