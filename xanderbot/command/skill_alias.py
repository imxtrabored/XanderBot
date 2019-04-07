from command.cmd_default import CmdDefault
from command.common import DiscordData, ReplyPayload, filter_name
from feh.unitlib import UnitLib


class SkillAlias(CmdDefault):

    LOGGING = True

    help_text = (
        'The ``skillalias`` command adds alternate skill name aliases to my '
        'database for more convenient searching. To add aliases for skill '
        'names, see the ``addalias`` command instead.\n\n'
        'Usage:\n'
        'Normal Mode: ``f?skillalias {name1}, {name2}``\n'
        'Bulk Mode: ``f?skillalias {existing name}, {new name 1}, {new name 2}, '
        '{additional names...}\n\n'
        'In normal mode, so long as one of the two provided names is currently '
        'valid and the other is not in my database, the invalid name will be '
        'added as an alias for the valid skill.\n\n'
        'In bulk mode, the first name provided must be valid. The command will '
        'try each new name against the database and add each one that does not '
        'exist to the database.\n\n'
        'Guidelines: Avoid adding meme names or foreign language names, as '
        'those could be confusing to other users. However, any name that is '
        'widely used amongst the English-speaking fanbase is acceptable even '
        'if it violates those guidelines\n'
        'Examples of acceptable names: LnD, RedBlade\n'
        'Examples of names to avoid: angery'
    )

    @staticmethod
    async def cmd(params, user_id):
        tokens = params.split(',')
        names = [
            filter_name(n)
            for n in tokens
        ]
        if len(names) < 2:
            return ReplyPayload(
                content='Not enough names entered. '
                'Please enter at least two names, separated by commas.'
            )
        skills = [UnitLib.get_skill(n) for n in names]
        if len(names) == 2:
            if skills[0] and not skills[1]:
                UnitLib.insert_skill_alias(skills[0], names[1])
                content = (f'Added alias {tokens[1].strip()} for '
                           f'{skills[0].name}.')
                await DiscordData.devs[0].send(
                    #f'{message.author.name}#{message.author.discriminator} '
                    f'added alias {names[1]} for {skills[0].name}.')
            elif skills[1] and not skills[0]:
                UnitLib.insert_skill_alias(skills[1], names[0])
                content = (f'Added alias {tokens[0].strip()} for '
                           f'{skills[1].name}.')
                await DiscordData.devs[0].send(
                    #f'{message.author.name}#{message.author.discriminator} '
                    f'added alias {names[0]} for {skills[1].name}.')
            elif skills[0] and skills[1]:
                content = 'All names are already skill aliases!'
            else:
                content = 'Cannot find a valid skill name; need at least one.'
        elif len(names) > 2:
            if not skills[0]:
                content = f'{tokens[0]} is not a valid skill.'
            else:
                added_names = [
                    name for name in names[1:]
                    if UnitLib.insert_skill_alias(skills[0], name)
                ]
                if added_names:
                    name_list = ', '.join(added_names)
                    content = (
                        f'Added aliases for {skills[0].short_name}:\n'
                        f'{name_list}'
                    )
                    await DiscordData.devs[0].send(
                        f'added aliases for {skills[0].short_name}:\n'
                        f'{name_list}')
                else: content = 'All names are already aliases.'
        return ReplyPayload(content=content)
