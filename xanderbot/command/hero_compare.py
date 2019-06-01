from collections import Counter

from discord import Embed

from command.cmd_default import CmdDefault
from command.common import (
    ReplyPayload, filter_name, process_hero, process_hero_args)
from command.hero_stats import HeroStats
from feh.currency import Dragonflower
from feh.emojilib import EmojiLib as em
from feh.hero import Rarity, Stat, SummonerSupport
from feh.unitlib import UnitLib


class HeroCompare(CmdDefault):

    help_text = (
        'The ``compare`` (alias ``c``) command quickly compares the '
        'attributes between two or more heroes.\n\n'
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
    def format_compare(embed, heroes, zoom_state):
        embed.clear_fields()
        if not heroes:
            embed.description = 'No heroes found.'
            return embed
        if len(heroes) == 1:
            embed.set_thumbnail(
                url='https://raw.githubusercontent.com/imxtrabored/XanderBot/'
                f'master/xanderbot/feh/data/heroes/{heroes[0].index}/Face.png')
            return HeroStats.format_stats(embed, heroes[0], zoom_state)
        elif len(heroes) == 2:
            title = (f'Comparing {heroes[0].short_name} '
                     f'and {heroes[1].short_name}:')
        else:
            title = f'Comparing {", ".join([h.short_name for h in heroes])}:'
        embed.add_field(name=title, value='-', inline=False)
        for hero in heroes:
            superboons = [
                '' if x == 0 else ' (+)' if x > 0 else ' (-)'
                for x in hero.get_boons_banes()
            ]
            if hero.boon is not Stat.NONE and hero.bane is not Stat.NONE:
                if hero.merges == 0:
                    ivs = f'\n(+{hero.boon.short}/-{hero.bane.short})'
                else:
                    ivs = f'\n(+{hero.boon.short}/~~-{hero.bane.short}~~)'
            else:
                ivs = ''
            if any(hero.equipped):
                equipped = (
                    f'{"".join([str(sk.icon) for sk in hero.equipped])}'
                    '\n'
                )
            else:
                equipped = ''
            final_stats = (
                f'{hero.rarity}{em.get(Rarity(hero.rarity))} '
                f'LV. {hero.level}+{hero.merges} · '
                f'{em.get(Dragonflower.get_move(hero.move_type))}'
                f'+{hero.flowers}{ivs}\n{equipped}'
                f'{em.get(Stat.HP)} HP: '
                f'{hero.final_hp}{superboons[0]}\n'
                f'{em.get(Stat.ATK)} Attack: '
                f'{hero.final_atk}{superboons[1]}\n'
                f'{em.get(Stat.SPD)} Speed: '
                f'{hero.final_spd}{superboons[2]}\n'
                f'{em.get(Stat.DEF)} Defense: '
                f'{hero.final_def}{superboons[3]}\n'
                f'{em.get(Stat.RES)} Resistance: '
                f'{hero.final_res}{superboons[4]}\n\n'
                f'Total: {hero.final_total}'
            )
            support = (em.get(SummonerSupport(hero.summ_support))
                       if hero.summ_support > 0 else '')
            embed.add_field(
                name = (
                    f'{hero.short_name} {em.get(hero.weapon_type)}'
                    f'{em.get(hero.move_type)}{support}'
                ),
                value = final_stats,
                inline = True
            )
        if len(heroes) == 2:
            stat_sort = sorted(heroes, key=lambda h: h.final_hp, reverse=True)
            if stat_sort[0].final_hp > stat_sort[-1].final_hp:
                hp_str = (
                    f'{em.get(Stat.HP)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].final_hp - stat_sort[1].final_hp} '
                    'more HP.'
                )
            else:
                hp_str = f'{em.get(Stat.HP)} Equal HP'
            stat_sort = sorted(heroes, key=lambda h: h.final_atk, reverse=True)
            if stat_sort[0].final_atk > stat_sort[-1].final_atk:
                atk_str = (
                    f'{em.get(Stat.ATK)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].final_atk - stat_sort[1].final_atk} '
                    'more Attack.'
                )
            else:
                atk_str = f'{em.get(Stat.ATK)} Equal Attack.'
            stat_sort = sorted(heroes, key=lambda h: h.final_spd, reverse=True)
            if stat_sort[0].final_spd > stat_sort[-1].final_spd:
                spd_str = (
                    f'{em.get(Stat.SPD)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].final_spd - stat_sort[1].final_spd} '
                    'more Speed.'
                )
            else:
                spd_str = f'{em.get(Stat.SPD)} Equal Speed.'
            stat_sort = sorted(heroes, key=lambda h: h.final_def, reverse=True)
            if stat_sort[0].final_def > stat_sort[-1].final_def:
                def_str = (
                    f'{em.get(Stat.DEF)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].final_def - stat_sort[1].final_def} '
                    'more Defense.'
                )
            else:
                def_str = f'{em.get(Stat.DEF)} Equal Defense.'
            stat_sort = sorted(heroes, key=lambda h: h.final_res, reverse=True)
            if stat_sort[0].final_res > stat_sort[-1].final_res:
                res_str = (
                    f'{em.get(Stat.RES)} '
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].final_res - stat_sort[1].final_res} '
                    'more Resistance.'
                )
            else:
                res_str = f'{em.get(Stat.RES)} Equal Resistance.'
            stat_sort = sorted(
                heroes, key=lambda h: h.final_total, reverse=True)
            if stat_sort[0].final_total > stat_sort[1].final_total:
                total_str = (
                    f'{stat_sort[0].short_name} has '
                    f'{stat_sort[0].final_total - stat_sort[1].final_total} '
                    'more total stats.'
                )
            else:
                total_str = 'Equal stat total.'
        else:
            stat_sort = sorted(heroes, key=lambda h: h.final_hp, reverse=True)
            if stat_sort[0].final_hp > stat_sort[-1].final_hp:
                final_list = ", ".join([
                    h.short_name for h in heroes
                    if h.final_hp == stat_sort[0].final_hp])
                hp_str = (
                    f'{em.get(Stat.HP)} '
                    f'Greatest HP: {stat_sort[0].final_hp} '
                    f'({final_list})'
                )
            else:
                hp_str = f'{em.get(Stat.HP)} All heroes have equal HP.'
            stat_sort = sorted(heroes, key=lambda h: h.final_atk, reverse=True)
            if stat_sort[0].final_atk > stat_sort[-1].final_atk:
                final_list = ", ".join([
                    h.short_name for h in heroes
                    if h.final_atk == stat_sort[0].final_atk])
                atk_str = (
                    f'{em.get(Stat.ATK)} '
                    f'Greatest Attack: {stat_sort[0].final_atk} '
                    f'({final_list})'
                )
            else:
                atk_str = f'{em.get(Stat.ATK)} All heroes have equal Attack.'
            stat_sort = sorted(heroes, key=lambda h: h.final_spd, reverse=True)
            if stat_sort[0].final_spd > stat_sort[-1].final_spd:
                final_list = ", ".join([
                    h.short_name for h in heroes
                    if h.final_spd == stat_sort[0].final_spd])
                spd_str = (
                    f'{em.get(Stat.SPD)} '
                    f'Greatest Speed: {stat_sort[0].final_spd} '
                    f'({final_list})'
                )
            else:
                spd_str = f'{em.get(Stat.SPD)} All heroes have equal Speed.'
            stat_sort = sorted(heroes, key=lambda h: h.final_def, reverse=True)
            if stat_sort[0].final_def > stat_sort[-1].final_def:
                final_list = ", ".join([
                    h.short_name for h in heroes
                    if h.final_def == stat_sort[0].final_def])
                def_str = (
                    f'{em.get(Stat.DEF)} '
                    f'Greatest Defense: {stat_sort[0].final_def} '
                    f'({final_list})'
                )
            else:
                def_str = f'{em.get(Stat.DEF)} All heroes have equal Defense.'
            stat_sort = sorted(heroes, key=lambda h: h.final_res, reverse=True)
            if stat_sort[0].final_res > stat_sort[-1].final_res:
                final_list = ", ".join([
                    h.short_name for h in heroes
                    if h.final_res == stat_sort[0].final_res])
                res_str = (
                    f'{em.get(Stat.RES)} '
                    f'Greatest Resistance: {stat_sort[0].final_res} '
                    f'({final_list})'
                )
            else:
                res_str = (
                    f'{em.get(Stat.RES)} All heroes have equal Resistance.')
            stat_sort = sorted(heroes, key=lambda h: h.final_total, reverse=True)
            if stat_sort[0].final_total > stat_sort[-1].final_total:
                final_list = ", ".join([
                    h.short_name for h in heroes
                    if h.final_total == stat_sort[0].final_total])
                total_str = (
                    f'Greatest stat total: {stat_sort[0].final_total} '
                    f'({final_list})'
                )
            else:
                total_str = 'All heroes have equal stat totals.'
        embed.add_field(
            name='Analysis:',
            value=(f'{hp_str}\n{atk_str}\n{spd_str}\n'
                   f'{def_str}\n{res_str}\n\n{total_str}'),
            inline=True
        )
        embed.color = em.get_color(None)
        return embed


    @staticmethod
    async def cmd(params, user_id):
        if not params:
            return ReplyPayload(
                content='No input. Please enter at least two heroes.')
        zoom_state = False
        embed = Embed()
        bad_args = []
        not_allowed = []
        if ';' in params:
            # fastest mode
            heroes, bad_args, not_allowed, no_commas = zip(*[
                process_hero(param, user_id) for param in params.split(';')])
            heroes = list(filter(None, heroes))
            bad_args = [arg for arg_list in bad_args for arg in arg_list]
            not_allowed = [arg for arg_list in not_allowed for arg in arg_list]
        elif ',' in params:
            # slow mode
            params = params.split(',')
            heroes = []
            for param in params:
                this_hero, bad_arg, n_allow, no_commas = process_hero(
                    param, user_id)
                if this_hero:
                    heroes.append(this_hero)
                    bad_args.extend(bad_arg)
                    not_allowed.extend(n_allow)
                else:
                    if not heroes:
                        bad_args.append(param)
                    else:
                        heroes[-1], bad_arg, n_allow = process_hero_args(
                            heroes[-1], (param,), user_id, defer_iv_match=True)
                        bad_args.extend(bad_arg)
                        not_allowed.extend(n_allow)
            for hero in heroes:
                if hero.boon == Stat.NONE and hero.bane != Stat.NONE:
                    hero.update_stat_mods(bane=Stat.NONE)
                elif hero.boon != Stat.NONE and hero.bane == Stat.NONE:
                    if hero.boon != Stat.HP:
                        hero.update_stat_mods(boon=Stat.HP)
                    else:
                        hero.update_stat_mods(boon=Stat.RES)
            embed.set_footer(
                text=('Please delimit compared heroes with semicolons (;) '
                      'in the future to improve speed and clarity.')
            )
        else:
            # slowest mode
            params = [filter_name(param) for param in params.split()]
            heroes = []
            ctr = 0
            while ctr < len(params):
                if heroes:
                    hero, bad_arg, n_allow = process_hero_args(
                        heroes[-1], (params[ctr],), user_id,
                        defer_iv_match=True)
                    if not bad_arg:
                        not_allowed.extend(n_allow)
                        ctr += 1
                        continue
                match_hero = None
                match_hero_index = 0
                for i in range(1, len(params[ctr:]) + 1):
                    hero = UnitLib.get_hero(
                        ''.join(params[ctr:ctr + i]), user_id)
                    if hero:
                        match_hero = hero
                        match_hero_index = i
                if match_hero:
                    heroes.append(match_hero)
                    ctr += match_hero_index
                else:
                    bad_args.append(params[ctr])
                    ctr += 1
            for hero in heroes:
                if hero.boon == Stat.NONE and hero.bane != Stat.NONE:
                    hero.update_stat_mods(bane=Stat.NONE)
                elif hero.boon != Stat.NONE and hero.bane == Stat.NONE:
                    if hero.boon != Stat.HP:
                        hero.update_stat_mods(bane=Stat.HP)
                    else:
                        hero.update_stat_mods(bane=Stat.RES)
            embed.set_footer(
                text=('Please delimit compared heroes with semicolons (;) '
                      'in the future to improve speed and clarity.')
            )
        # modify duplicate hero names (detect dupes using id)
        for hero in heroes:
            if hero.custom_name:
                hero.short_name = f'{hero.custom_name} [{hero.short_name}]'
        counts = {k:v for k, v in
                  Counter([h.short_name for h in heroes]).items()
                  if v > 1}
        for i in reversed(range(len(heroes))):
            item = heroes[i].short_name
            if item in counts and counts[item]:
                heroes[i].short_name = (
                    f'{heroes[i].short_name} ({counts[item]})')
                counts[item] -= 1
        embed = HeroCompare.format_compare(embed, heroes, zoom_state)
        err_text = []
        if any(bad_args):
            err_text.append('I did not understand the following: '
                            f'{", ".join(bad_args)}')
        if any(not_allowed):
            err_text.append('The following skills are unavailable for this '
                            f'hero: {", ".join(not_allowed)}')
        content = '\n'.join(err_text)
        return ReplyPayload(content=content, embed=embed)
