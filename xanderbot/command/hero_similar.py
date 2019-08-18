from dataclasses import dataclass

from discord import Embed

from command.cmd_default import CmdDefault
from command.common import (
    ReactMenu, ReplyPayload, ReactEditPayload, process_hero)
from feh.emojilib import EmojiLib as em
from feh.unitlib import UnitLib


PAGE_LIMIT = 24


class HeroSimilar(CmdDefault):

    help_text = (
        'The ``list`` command (aliases ``hl``, ``hs``) lists all heroes that '
        'match the provided search parameters.\n\n'
        'Usage: ``f?list {search params}``\n\n'
        'For a similar search that lets you sort heroes by their attributes, '
        'see the ``sort`` command, which operates similarly to this command.'
        '\n\n'
        'Special syntax for search:\n'
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
        '⬆',
        '⬇',
    )

    @dataclass
    class Data(object):

        __slots__ = (
            'embed', 'results', 'search_param', 'page_start'
        )

        embed: Embed
        results: list
        search_param: str
        page_start: int

    @staticmethod
    def format_list(embed, results, search_hero, start=0):
        if not results:
            start = -1
            end = 0
            result = 'No results!'
        else:
            end = min(start + PAGE_LIMIT, len(results))
            result = '\n'.join(results[start:end])
        matching = f''
        embed.title = (
            f'Heroes with similar stats to {search_hero.short_name} '
            f'({start + 1} - {end} of {len(results)}):'
        )
        embed.description = result
        return embed

    @staticmethod
    async def cmd(params, user_id):
        if not params:
            return ReplyPayload(
                content='No input. Please enter a hero.',
                reactable=ReactMenu(
                    emojis=HeroSimilar.REACT_MENU, callback=HeroArt.react)
            )
        hero, bad_args, not_allowed, no_commas = process_hero(params, user_id)
        if not hero:
            return ReplyPayload(
                content=(
                    f'Hero not found: {bad_args[0]}. Don\'t forget that '
                    'modifiers should be delimited by commas.'
                ),
                reactable=ReactMenu(
                    emojis=HeroSimilar.REACT_MENU, callback=HeroSimilar.react),
            )
        result_list = UnitLib.sort_SSD(hero)
        embed = Embed()
        HeroSimilar.format_list(
            embed, result_list, hero, 0)
        if any(bad_args):
            content = ('I did not understand the following: '
                       f'{", ".join(bad_args)}')
        else:
            content = ''
        embed.color = em.get_color(None)
        react_menu = ReactMenu(
            emojis=HeroSimilar.REACT_MENU,
            data=HeroSimilar.Data(embed, result_list, params, 0),
            callback=HeroSimilar.react,
        )
        return ReplyPayload(content=content, embed=embed, reactable=react_menu)

    @staticmethod
    async def react(reaction, data, user_id):
        if not data:
            return ReactEditPayload(delete=True)
        if reaction.emoji == '⬆':
            if data.page_start > 0:
                page_size = PAGE_LIMIT
                data.page_start = max(data.page_start - page_size, 0)
            else:
                return ReactEditPayload(delete=True)
        elif reaction.emoji == '⬇':
            page_size = PAGE_LIMIT
            new_start = data.page_start + page_size
            if new_start < len(data.results):
                data.page_start = new_start
            else:
                return ReactEditPayload(delete=True)
        else:
            return ReactEditPayload()
        HeroSimilar.format_list(data.embed, data.results, data.search_param,
                             data.page_start)
        return ReactEditPayload(embed=data.embed, delete=True)
