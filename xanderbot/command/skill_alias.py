from command.cmd_default import CmdDefault
from command.common import DiscordData, filter_name
from feh.unitlib import UnitLib


class SkillAlias(CmdDefault):

    help_text = (
        'The ``skillalias`` command adds alternate skill name aliases to my '
        'database for more convenient searching. To add aliases for skill '
        'names, see the ``addalias`` command instead.\n\n'
        'Usage: ``f?skillalias {name1}, {name2}``\n\n'
        'So long as one of the two provided names is currently valid and the '
        'other is not in my database, the invalid name will be added as an '
        'alias for the valid skill.\n\n'
        'Guidelines: Avoid adding meme names or foreign language names, as '
        'those could be confusing to other users. However, any name that is '
        'widely used amongst the English-speaking fanbase is acceptable even '
        'if it violates those guidelines\n'
        'Examples of acceptable names: LnD, RedBlade\n'
        'Examples of names to avoid: angery'
    )

    @staticmethod
    async def cmd(params):
        tokens = params.split(',')
        names = [
            filter_name(n)
            for n in tokens
        ]
        if len(names) != 2:
            return (
                'Wrong number of names found. '
                'Please enter two names, separated by a comma.',
                None, None
            )
        skills = [UnitLib.get_skill(n) for n in names]
        if skills[0] and not skills[1]:
            UnitLib.insert_skill_alias(skills[0], names[1])
            content = f'Added alias {tokens[1]} for {skills[0].name}.'
            await DiscordData.devs[0].send(
                #f'{message.author.name}#{message.author.discriminator} '
                f'added alias {names[1]} for {skills[0].name}.')
        elif skills[1] and not skills[0]:
            UnitLib.insert_skill_alias(skills[1], names[0])
            content = f'Added alias {tokens[0]} for {skills[1].name}.'
            await DiscordData.devs[0].send(
                #f'{message.author.name}#{message.author.discriminator} '
                f'added alias {names[0]} for {skills[1].name}.')
        elif skills[0] and skills[1]:
            content = 'All names are already skill aliases!'
        else:
            content = 'Cannot find a valid skill name; need at least one.'
        return content, None, None
