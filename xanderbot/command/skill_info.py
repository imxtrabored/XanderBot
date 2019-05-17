from dataclasses import dataclass

from discord import Embed

from command.cmd_default import CmdDefault
from command.common import ReactMenu, ReplyPayload, ReactEditPayload
from feh.emojilib import EmojiLib as em
from feh.hero import MoveType, Rarity
from feh.skill import Skill, SkillType, SkillWeaponGroup
from feh.unitlib import UnitLib


class SkillInfo(CmdDefault):

    help_text = (
        'The ``skill`` command displays details about a skill (weapons, '
        'assists, specials, passives, or sacred seals).\n\n'
        'Usage: ``f?skill {skill name}``\n\n'
        'Note: To display information on the skills known by a hero, by '
        'default, use the ``skills`` (with an s) command.'
    )

    @dataclass
    class Data(object):
        __slots__ = ('embed', 'skill', 'zoom_state', 'progression')
        embed: Embed
        skill: Skill
        zoom_state: bool
        progression: dict

    REACT_MENU = (
        '🔍',
        '⬆',
        '⬇',
    )

    @staticmethod
    def format_eff(skill):
        if any((
                skill.eff_infantry,
                skill.eff_armor   ,
                skill.eff_cavalry ,
                skill.eff_flier   ,
                skill.eff_magic   ,
                skill.eff_dragon  ,
        )):
            eff_list = [' Eff: ']
            if skill.eff_infantry: eff_list.append(str(em.get(MoveType.INFANTRY)))
            if skill.eff_armor   : eff_list.append(str(em.get(MoveType.ARMOR   )))
            if skill.eff_cavalry : eff_list.append(str(em.get(MoveType.CAVALRY )))
            if skill.eff_flier   : eff_list.append(str(em.get(MoveType.FLIER   )))
            if skill.eff_magic   :
                eff_list.append(str(em.get(SkillWeaponGroup.R_TOME)))
                eff_list.append(str(em.get(SkillWeaponGroup.B_TOME)))
                eff_list.append(str(em.get(SkillWeaponGroup.G_TOME)))
            if skill.eff_dragon  : eff_list.append(str(em.get(SkillWeaponGroup.S_BREATH)))
            effective = ''.join(eff_list)
        else: effective = ''
        return effective

    @staticmethod
    def format_skill(embed, skill, zoom_state):
        embed.clear_fields()
        type_icon = (em.get(skill.weapon_type)
                     if skill.weapon_type else em.get(skill.skill_type))
        seal_icon = (
            em.get(SkillType.PASSIVE_SEAL)
            if skill.skill_type != SkillType.PASSIVE_SEAL and skill.is_seal
            else ""
        )
        title = f'{skill.icon} {skill.name} · {type_icon}{seal_icon}'
        if (skill.skill_type == SkillType.WEAPON
                or skill.skill_type == SkillType.WEAPON_REFINED
           ):
            effective = SkillInfo.format_eff(skill)
            if skill.refine_path:
                refine_stats = ''.join((
                    f'{f" HP+{skill.bonus_hp}" if skill.bonus_hp else ""}',
                    f'{f" Spd+{skill.bonus_spd}" if skill.bonus_spd else ""}',
                    f'{f" Def+{skill.bonus_def}" if skill.bonus_def else ""}',
                    f'{f" Res+{skill.bonus_res}" if skill.bonus_res else ""}',
                 ))
            else:
                refine_stats = ''
            weapon_desc = (f'Mt: {skill.might} '
                           f'Rng: {skill.range}{effective}{refine_stats}')
        elif skill.skill_type == SkillType.SPECIAL:
            weapon_desc = f'{em.get(SkillType.SPECIAL)} {skill.special_cd}'
        else:
            weapon_desc = None
        prereq = (
            '_This skill can only be equipped by its original unit._'
            if skill.exclusive else
            f'**Requires:** {skill.prereq1.icon} {skill.prereq1.name} '
            f'or {skill.prereq2.icon} {skill.prereq2.name}'
            if skill.prereq2 else
            f'**Requires:** {skill.prereq1.icon} {skill.prereq1.name}'
            if skill.prereq1
            else None
        )
        if (skill.skill_type != SkillType.WEAPON
                and skill.skill_type != SkillType.WEAPON_REFINED):
            if skill.is_staff:
                restrictions = (
                    "_This skill can only be equipped by staff users._")
            else:
                if skill.restrict_from:
                    restrict_list = [
                        str(em.get(type)) for type in skill.restrict_from]
                    restrictions = f'**Cannot use:** {"".join(restrict_list)}'
                else: restrictions = None
        else:
            restrictions = None
        if zoom_state and not skill.exclusive:
            sp = f'**SP:** {skill.sp} ({skill.sp * 3 // 2})'
        else:
            sp = f'**SP:** {skill.sp}'
        if zoom_state:
            if skill.postreq:
                postreq_list = [
                    f'{postreq.icon} {postreq.name}'
                    for postreq in skill.postreq if not postreq.exclusive
                ]
                prf_postreq_count = len(skill.postreq) - len(postreq_list)
                # optimize note?
                postreq_str = (', '.join(postreq_list)
                if len(skill.postreq) - prf_postreq_count < 10
                else ', '.join([
                    f'{postreq.name}'
                    for postreq in skill.postreq
                    if not postreq.exclusive
                ]))
                prf_postreqs = (f' and {prf_postreq_count} Prf skills.'
                                if prf_postreq_count else '')
            else:
                postreq_str = 'None'
                prf_postreqs = ''
            postreqs = f'**Required for:** {postreq_str}{prf_postreqs}'
            cumul_sp = skill.get_cumul_sp_recursive()
            skill_cumul_sp = (
                f'**Cumulative SP:** {cumul_sp}'
                f'{f" ({cumul_sp * 3 // 2})" if not skill.exclusive else ""}'
            )
            if skill.evolves_from:
                evolve_src = (
                    '**Evolves from:** '
                    f'{skill.evolves_from.icon} {skill.evolves_from.name}')
            else: evolve_src = None
        else:
            postreqs, skill_cumul_sp, evolve_src = None, None, None
        description = '\n'.join(filter(None, [
            weapon_desc,
            skill.description,
            prereq,
            restrictions,
            sp,
            skill_cumul_sp,
            evolve_src,
            postreqs,
        ]))
        embed.add_field(name=title, value=description, inline=False)
        if skill.skill_type == SkillType.PASSIVE_SEAL:
            learnable = ''
        else:
            learnable_count = (
                len(skill.learnable[1]) + len(skill.learnable[2])
                + len(skill.learnable[3]) + len(skill.learnable[4])
                + len(skill.learnable[5])
            )
            if (skill.skill_type == SkillType.WEAPON and not skill.exclusive
                    and ((skill.tier <= 2 and not skill.is_staff)
                         or skill.tier <= 1)):
                learnable = 'Basic weapon available to most eligible heroes.'
            elif (skill.skill_type == SkillType.ASSIST and skill.is_staff
                  and skill.tier <= 1):
                learnable = 'Basic assist available to all staff users.'
            #elif reduce(lambda x, y: x + len(y), skill.learnable[1:], 0) > 20:
            elif learnable_count > 25:
                learnable = (
                    f'{learnable_count} different heroes know this skill.')
            elif learnable_count == 0:
                learnable = 'None'
            else:
                learnable = '\n'.join([
                    f'{count}{em.get(Rarity(count))}: '
                    f'{", ".join([hero.short_name for hero in hero_list])} '
                    f'[{len(hero_list)}]'
                    for count, hero_list in enumerate(skill.learnable[1:], 1)
                    if hero_list
                ])
        embed.add_field(name='Available from:', value=learnable, inline=False)
        if skill.refinable or skill.evolves_to:
            if zoom_state:
                refine_secondary = (
                    f', {skill.refine_stones} '
                    f'{em.get("Currency_Refining_Stone")}'
                    if skill.refine_stones else
                    f', {skill.refine_dew} '
                    f'{em.get("Currency_Divine_Dew")}'
                    if skill.refine_dew else ''
                )
                refine_cost = (
                    f' {skill.refine_sp} SP, '
                    f'{skill.refine_medals} '
                    f'{em.get("Currency_Arena_Medal")}'
                    f'{refine_secondary}'
                )
            else: refine_cost = ''
            refine_header = (f'**Refine options:**{refine_cost}'
                             if skill.refinable else None)
            if skill.refined_ver and not skill.is_refined_variant:
                refined_skill = skill.refined_ver
                refined_title = (f'Weapon Refinery\n{refined_skill.icon} '
                                 f'Refined {skill.name} · {type_icon}')
                effective = SkillInfo.format_eff(refined_skill)
                refined_w_desc = (
                    f'Mt: {refined_skill.might} '
                    f'Rng: {refined_skill.range}{effective}'
                    if (refined_skill.skill_type == SkillType.WEAPON
                        or refined_skill.skill_type == SkillType.WEAPON_REFINED
                       )
                    else None
                )
                refined_skill_str = '\n'.join(filter(None, (
                    refined_w_desc, refined_skill.description
                )))
            else:
                refined_title = 'Weapon Refinery'
                refined_skill_str = None

            refine_eff = (f'{skill.refine_eff.icon}: '
                          f'{skill.refine_eff.description}'
                          if skill.refine_eff else None)
            skill_refines = (
                skill.refine_st1,
                skill.refine_st2,
                skill.refine_atk,
                skill.refine_spd,
                skill.refine_def,
                skill.refine_res,
            )
            if zoom_state:
                generic_refines = '\n'.join([
                    f'{refine.icon}: {refine.description}'
                    for refine in skill_refines
                    if refine
                ])
            else:
                generic_refines = ' · '.join([
                    str(refine.icon)
                    for refine in skill_refines
                    if refine
                ])
            if zoom_state and skill.evolves_to:
                evolve_secondary = (
                    f', {skill.evolve_stones} '
                    f'{em.get("Currency_Refining_Stone")}'
                    if skill.evolve_stones else
                    f', {skill.evolve_dew} '
                    f'{em.get("Currency_Divine_Dew")}'
                    if skill.evolve_dew else ''
                )
                evolve_cost = (
                    f': {skill.evolves_to.sp} SP, '
                    f'{skill.evolve_medals} '
                    f'{em.get("Currency_Arena_Medal")}'
                    f'{evolve_secondary}'
                )
            else:
                evolve_cost = ''
            evolution = (
                f'**Evolves into:** '
                f'{skill.evolves_to.icon} {skill.evolves_to.name}'
                f'{evolve_cost}'
                if skill.evolves_to else None
            )
            refine_desc = '\n'.join(filter(None, [
                refined_skill_str,
                refine_header,
                refine_eff,
                generic_refines,
                evolution,
            ]))
            embed.add_field(
                name=refined_title, value=refine_desc, inline=False)
        if (skill.skill_type == SkillType.WEAPON
                or skill.skill_type == SkillType.WEAPON_REFINED
                or (skill.skill_type == SkillType.ASSIST and skill.is_staff)
        ):
            embed.set_thumbnail(
                url=('https://raw.githubusercontent.com/imxtrabored/XanderBot/'
                     f'master/xanderbot/feh/data/skills/{skill.index}.png')
            )
        else: embed.set_thumbnail(
            url=f'https://cdn.discordapp.com/emojis/{skill.icon.id}.png')
        if skill.weapon_type:
            embed.color = em.get_color(skill.weapon_type)
        else:
            embed.color = em.get_color(skill.skill_type)
        return embed


    @staticmethod
    async def cmd(params, user_id):
        if not params:
            return ReplyPayload(
                content='No input. Please enter a skill name.',
                reactable=ReactMenu(
                    emojis=SkillInfo.REACT_MENU, callback=SkillInfo.react)
            )
        tokens = params.split(',')
        skill = UnitLib.get_skill(tokens[0])
        if not skill:
            return ReplyPayload(
                content=(
                    f'Skill not found: {tokens[0]}.\n'
                    '(For information on the skills known by a hero by '
                    'default, use the ``skills`` (with an \'s\') command.)'
                ),
                reactable=ReactMenu(
                    emojis=SkillInfo.REACT_MENU, callback=SkillInfo.react),
            )
        embed = Embed()
        SkillInfo.format_skill(embed, skill, False)
        react_menu = ReactMenu(
            emojis=SkillInfo.REACT_MENU,
            data=SkillInfo.Data(embed, skill, False, {skill.tier: skill}),
            callback=SkillInfo.react,
        )
        return ReplyPayload(embed=embed, reactable=react_menu)


    @staticmethod
    async def react(reaction, data, user_id):
        if not data:
            return ReactEditPayload(delete=True)
        if reaction.emoji == '🔍':
            data.zoom_state = not data.zoom_state
        elif reaction.emoji == '⬆':
            if data.skill.tier + 1 in data.progression:
                data.skill = data.progression[data.skill.tier + 1]
            elif data.skill.postreq:
                data.skill = data.skill.postreq[0]
                data.progression[data.skill.tier] = data.skill
            else:
                return ReactEditPayload(delete=True)
        elif reaction.emoji == '⬇':
            if data.skill.tier - 1 in data.progression:
                data.skill = data.progression[data.skill.tier - 1]
            elif data.skill.prereq1:
                data.skill = data.skill.prereq1
                data.progression[data.skill.tier] = data.skill
            else:
                return ReactEditPayload(delete=True)
        elif reaction.emoji == '👁':
            data.embed.set_author(name=str(data.skill.index))
        else:
            return ReactEditPayload()
        data.embed = SkillInfo.format_skill(
            data.embed, data.skill, data.zoom_state)
        return ReactEditPayload(embed=data.embed, delete=True)
