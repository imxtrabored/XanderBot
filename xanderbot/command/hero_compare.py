from collections import Counter
from operator import methodcaller

import discord

from command.cmd_default import CmdDefault
from command.common import process_hero
from command.hero_stats import HeroStats
from feh.emojilib import EmojiLib as em
from feh.hero import Rarity, Stat
from feh.unitlib import UnitLib


class HeroCompare(CmdDefault):

    help_text = (
        'The ``compare`` command quickly compares the attributes between two '
        'or more heroes.\n\n'
        'Usage: ``f?compare {hero 1}, {modifier 1}, {modifier 2}, {additional '
        'modifiers...}; {hero 2}, {modifier 1}, {modifier 2}, {etc...}; '
        '{additional heroes...}``\n\n'
        'Note that heroes are delimited by semicolons (;), while their '
        'modifiers are delimited by commas (,).\n\n'
        'Tip: The ``compare`` command can even compare a hero with themselves; '
        'for instance, comparing the same hero with different assets and '
        'flaws, or the same hero at different merge levels.'
    )

    @staticmethod
    def format_compare(heroes, embed, zoom_state):
        embed.clear_fields()
        if not heroes:
            embed.description = 'No heroes found.'
            return embed
        if   len(heroes) == 1:
            embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/heroes/{heroes[0].id}/Face.png')
            return HeroStats.format_stats(heroes[0], embed, zoom_state)
        elif len(heroes) == 2:
            title = (f'Comparing {heroes[0].short_name} '
                     f'and {heroes[1].short_name}:')
        else:
            title = f'Comparing {", ".join([h.short_name for h in heroes])}:'
        embed.add_field(
            name = title,
            value = '-',
            inline = False
        )
        for hero in heroes:
            superboons = [
                '' if x == 0 else ' (+)' if x > 0 else ' (-)'
                for x in hero.get_boons_banes()
            ]
            max_stats = (
                f'{hero.rarity}{em.get(Rarity(hero.rarity))} '
                f'LV. {hero.level}+{hero.merges}, DF: {hero.flowers}\n'
                f'{em.get(Stat.HP)} HP: '
                f'{hero.max_hp}{superboons[0]}\n'
                f'{em.get(Stat.ATK)} Attack: '
                f'{hero.max_atk}{superboons[1]}\n'
                f'{em.get(Stat.SPD)} Speed: '
                f'{hero.max_spd}{superboons[2]}\n'
                f'{em.get(Stat.DEF)} Defense: '
                f'{hero.max_def}{superboons[3]}\n'
                f'{em.get(Stat.RES)} Resistance: '
                f'{hero.max_res}{superboons[4]}\n\n'
                f'BST: {hero.max_total}'
            )

            embed.add_field(
                name = (
                    f'{hero.short_name} '
                    f'{em.get(hero.weapon_type)} '
                    f'{em.get(hero.move_type)} '
                ),
                value = max_stats,
                inline = True
            )
        if len(heroes) == 2:
            stat_sort = sorted(heroes,
                               key = lambda h: h.max_hp,
                               reverse = True)
            if stat_sort[0].max_hp > stat_sort[-1].max_hp:
                hp_str = (
                    f'{em.get(Stat.HP)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_hp - stat_sort[1].max_hp} '
                    'more HP.'
                )
            else: hp_str = f'{em.get(Stat.HP)} Equal HP'
            stat_sort = sorted(heroes,
                               key = lambda h: h.max_atk,
                               reverse = True)
            if stat_sort[0].max_atk > stat_sort[-1].max_atk:
                atk_str = (
                    f'{em.get(Stat.ATK)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_atk - stat_sort[1].max_atk} '
                    'more Attack.'
                )
            else: atk_str = f'{em.get(Stat.ATK)} Equal Attack.'
            stat_sort = sorted(heroes,
                               key = lambda h: h.max_spd,
                               reverse = True)
            if stat_sort[0].max_spd > stat_sort[-1].max_spd:
                spd_str = (
                    f'{em.get(Stat.SPD)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_spd - stat_sort[1].max_spd} '
                    'more Speed.'
                )
            else: spd_str = f'{em.get(Stat.SPD)} Equal Speed.'
            stat_sort = sorted(heroes,
                               key = lambda h: h.max_def,
                               reverse = True)
            if stat_sort[0].max_def > stat_sort[-1].max_def:
                def_str = (
                    f'{em.get(Stat.DEF)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_def - stat_sort[1].max_def} '
                    'more Defense.'
                )
            else: def_str = f'{em.get(Stat.DEF)} Equal Defense.'
            stat_sort = sorted(heroes,
                               key = lambda h: h.max_res,
                               reverse = True)
            if stat_sort[0].max_res > stat_sort[-1].max_res:
                res_str = (
                    f'{em.get(Stat.RES)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_res - stat_sort[1].max_res} '
                    'more Resistance.'
                )
            else: res_str = f'{em.get(Stat.RES)} Equal Resistance.'
            stat_sort = sorted(heroes,
                               key = lambda h: h.max_total,
                               reverse = True)
            if stat_sort[0].max_total > stat_sort[1].max_total:
                total_str = (
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].max_total - stat_sort[1].max_total} '
                    'more total stats.'
                )
            else: total_str = 'Equal stat total.'
        else:
            stat_sort = sorted(heroes,
                               key = lambda h: h.max_hp,
                               reverse = True)
            if stat_sort[0].max_hp > stat_sort[-1].max_hp:
                max_list = ", ".join([
                    h.short_name for h in heroes
                    if h.max_hp == stat_sort[0].max_hp])
                hp_str = (
                    f'{em.get(Stat.HP)} '
                    f'Greatest HP: {stat_sort[0].max_hp} '
                    f'({max_list})'
                )
            else: hp_str = (f'{em.get(Stat.HP)} '
                            'All heroes have equal HP.')
            stat_sort = sorted(heroes,
                               key = lambda h: h.max_atk,
                               reverse = True)
            if stat_sort[0].max_atk > stat_sort[-1].max_atk:
                max_list = ", ".join([
                    h.short_name for h in heroes
                    if h.max_atk == stat_sort[0].max_atk])
                atk_str = (
                    f'{em.get(Stat.ATK)} '
                    f'Greatest Attack: {stat_sort[0].max_atk} '
                    f'({max_list})'
                )
            else: atk_str = (f'{em.get(Stat.ATK)} '
                             'All heroes have equal Attack.')
            stat_sort = sorted(heroes,
                               key = lambda h: h.max_spd,
                               reverse = True)
            if stat_sort[0].max_spd > stat_sort[-1].max_spd:
                max_list = ", ".join([
                    h.short_name for h in heroes
                    if h.max_spd == stat_sort[0].max_spd])
                spd_str = (
                    f'{em.get(Stat.SPD)} '
                    f'Greatest Speed: {stat_sort[0].max_spd} '
                    f'({max_list})'
                )
            else: spd_str = (f'{em.get(Stat.SPD)} '
                             'All heroes have equal Speed.')
            stat_sort = sorted(heroes,
                               key = lambda h: h.max_def,
                               reverse = True)
            if stat_sort[0].max_def > stat_sort[-1].max_def:
                max_list = ", ".join([
                    h.short_name for h in heroes
                    if h.max_def == stat_sort[0].max_def])
                def_str = (
                    f'{em.get(Stat.DEF)} '
                    f'Greatest Defense: {stat_sort[0].max_def} '
                    f'({max_list})'
                )
            else: def_str = (f'{em.get(Stat.DEF)} '
                             'All heroes have equal Defense.')
            stat_sort = sorted(heroes,
                               key = lambda h: h.max_res,
                               reverse = True)
            if stat_sort[0].max_res > stat_sort[-1].max_res:
                max_list = ", ".join([
                    h.short_name for h in heroes
                    if h.max_res == stat_sort[0].max_res])
                res_str = (
                    f'{em.get(Stat.RES)} '
                    f'Greatest Resistance: {stat_sort[0].max_res} '
                    f'({max_list})'
                )
            else: res_str = (f'{em.get(Stat.RES)} '
                             'All heroes have equal Resistance.')
            stat_sort = sorted(heroes,
                               key = lambda h: h.max_total,
                               reverse = True)
            if stat_sort[0].max_total > stat_sort[-1].max_total:
                max_list = ", ".join([
                    h.short_name for h in heroes
                    if h.max_total == stat_sort[0].max_total])
                total_str = (
                    f'Greatest stat total: {stat_sort[0].max_total} '
                    f'({max_list})'
                )
            else: total_str = 'All heroes have equal stat totals.'
        embed.add_field(
            name = 'Analysis:',
            value = (f'{hp_str}\n{atk_str}\n{spd_str}\n'
                     f'{def_str}\n{res_str}\n\n{total_str}'),
            inline = True
        )
        embed.color = em.get_color(None)
        return embed


    @staticmethod
    async def cmd(params):
        if not params:
            return 'No input detected!', None, [[], False]
        zoom_state = False
        embed = discord.Embed()
        bad_args = []
        if ';' not in params:
            # slow mode
            params = params.split(',')
            heroes = []
            for param in params:
                this_hero = UnitLib.get_hero(param)
                if this_hero: heroes.append(this_hero)
                else:
                    if not heroes:
                        bad_args.append(param)
                    else:
                        heroes[-1], bad_arg = process_hero(heroes[-1], [param])
                        bad_args.extend(bad_arg)

            embed.set_author(
                name = ('Please delimit compared heroes with semicolons (;) '
                        'in the future to improve speed and clarity.')
            )
        else:
            # normal mode
            hero_list = map(methodcaller('split', ','), params.split(';'))
            heroes = []
            for param in hero_list:
                this_hero = UnitLib.get_hero(param[0])
                if this_hero:
                    this_hero, bad_arg = process_hero(this_hero, param[1:])
                    heroes.append(this_hero)
                    bad_args.extend(bad_arg)
                else: bad_args.append(param[0])
        # modify duplicate hero names (detect dupes using id)
        counts = {k:v for k, v in
                  Counter([h.id for h in heroes]).items()
                  if v > 1}
        for i in reversed(range(len(heroes))):
            item = heroes[i].id
            if item in counts and counts[item]:
                heroes[i].short_name = (f'{heroes[i].short_name} '
                                        f'({counts[item]})')
                counts[item] -= 1
        embed = HeroCompare.format_compare(heroes, embed, zoom_state)

        if bad_args:
            content = ('I did not understand the following arguments: '
                       f'{", ".join(bad_args)}')
        else:
            content = ''
        return content, embed, [heroes, zoom_state]
