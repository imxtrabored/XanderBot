from dataclasses import dataclass

from discord import Embed

from command.cmd_default import CmdDefault
from command.common import ReactMenu, ReplyPayload, ReactEditPayload
from feh.emojilib import EmojiLib as em
from feh.unitlib import UnitLib

PAGE_LIMIT = 24
ZOOM_LIMIT = 12


class SkillSearch(CmdDefault):

    help_text = (
        'The ``skillsearch`` command searches for any skills that match the '
        'search terms, which can be part of their skill type, weapon type, '
        'description, or more.\n\n'
        'Usage: ``f?skillsearch {search terms}``\n\n'
        'Some skills are tagged with related skills, so ``skillsearch`` can '
        'find similar skills even if their names or wording are dissimilar.\n'
        '``skillsearch`` intentionally does not search all skills; it only '
        'searches maximum rank skills or otherwise interesting skills to '
        'reduce the number of redundant or duplicate results.\n\n'
        'Special syntax:\n'
        'The logical operators ``AND``, ``OR``, and ``NOT`` can be '
        'represented by the symbols ``&``, ``|``, and ``-``, respectively. '
        '``&`` is somewhat redundant as it is implicit between terms, but it '
        'is needed for logical groupings.\n'
        'Parentheses ``()`` can be used to logically group terms for logical '
        'operators. The implicit ``AND`` operator is NOT inserted before or '
        'after parenthetical statements.\n'
        'Double quotation marks (``"``) group terms together as a single '
        'string. For instance, ``turn 1`` will match any skills with "turn" '
        'and "1" anywhere in their description, but ``"turn 1"`` will only '
        'match skills with exactly "turn 1" in their description.\n'
        'The asterisk (``*``) symbol immediately following a term marks it as '
        'a prefix token. For instance, ``sword*`` will match any word that '
        'begins with "sword", such as "swordbreaker".\n'
        'If your search contains a syntax error, the search will be attempted '
        'with all special operators stripped out instead.'
    )

    REACT_MENU = (
        '🔍',
        '⬆',
        '⬇',
    )
    @dataclass
    class Data(object):

        __slots__ = (
            'embed', 'results', 'page_start', 'search_param', 'zoom_state'
        )

        embed: Embed
        results: list
        page_start: int
        search_param: str
        zoom_state: bool

    @staticmethod
    def format_search(results, embed, zoom_state, param, start=0):
        if not results:
            start = -1
            if 'fish' in param:
                end = '🐟'
                result = '🐟'
            else:
                end = 0
                result = 'No results!'
        elif zoom_state:
            end = min(start + ZOOM_LIMIT, len(results))
            result = '\n'.join(
                [''.join((str(row[0]), '__', row[1], '__\n', row[2]))
                 for row in results[start:end]]
            )
        else:
            end = min(start + PAGE_LIMIT, len(results))
            result = '\n'.join(
                [''.join((str(row[0]), row[1]))
                 for row in results[start:end]])
        embed.title = (f'Skills matching "{param}" '
                       f'({start + 1} - {end} of {len(results)}):')
        embed.description = result
        return embed

    @staticmethod
    async def cmd(params, user_id):
        if not params:
            return ReplyPayload(
                content='No input. Please enter search terms.',
                reactable=ReactMenu(
                    emojis=SkillSearch.REACT_MENU, callback=SkillSearch.react),
            )
        tokens = params.split(',')
        skill_list = UnitLib.search_skills(params)
        if skill_list is None:
            return ReplyPayload(
                content=('Syntax error. Ensure that your parentheses and '
                         'quotation marks match up, then try again.'),
                reactable=ReactMenu(
                    emojis=SkillSearch.REACT_MENU, callback=SkillSearch.react),
            )

        embed = Embed()
        SkillSearch.format_search(skill_list, embed, False, tokens[0], 0)
        embed.color = em.get_color(None)
        react_menu = ReactMenu(
            emojis=SkillSearch.REACT_MENU,
            data=SkillSearch.Data(embed, skill_list, 0, tokens[0], False),
            callback=SkillSearch.react,
        )
        return ReplyPayload(embed=embed, reactable=react_menu)

    @staticmethod
    async def react(reaction, data, user_id):
        if not data:
            return ReactEditPayload(delete=True)
        if reaction.emoji == '🔍':
            data.zoom_state = not data.zoom_state
        elif reaction.emoji == '⬆':
            if data.page_start > 0:
                if data.zoom_state:
                    page_size = ZOOM_LIMIT
                else:
                    page_size = PAGE_LIMIT
                data.page_start = max(data.page_start - page_size, 0)
            else:
                return ReactEditPayload(delete=True)
        elif reaction.emoji == '⬇':
            if data.zoom_state:
                page_size = ZOOM_LIMIT
            else:
                page_size = PAGE_LIMIT
            new_start = data.page_start + page_size
            if new_start < len(data.results):
                data.page_start = new_start
            else:
                return ReactEditPayload(delete=True)
        else:
            return ReactEditPayload()
        SkillSearch.format_search(data.results, data.embed, data.zoom_state,
                                  data.search_param, data.page_start)
        return ReactEditPayload(embed=data.embed, delete=True)
