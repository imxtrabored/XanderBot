import discord
from functools import reduce

from command.cmd_default import CmdDefault
from feh.emojilib import EmojiLib as em
from feh.hero import MoveType, Rarity
from feh.skill import SkillType, SkillWeaponGroup
from feh.unitlib import UnitLib


class SkillInfo(CmdDefault):

    help_text = (
        'The ``skill`` command displays details about a skill (weapons, '
        'assists, specials, passives, or sacred seals).\n\n'
        'Usage: ``f?skill {skill name}``\n\n'
        'Note: To display information on the skills known by a hero, by '
        'default, use the ``skills`` (with an s) command.'
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
    def format_skill(skill, embed, zoom_state):
        type_icon = (em.get(skill.weapon_type)
                     if skill.weapon_type else em.get(skill.type))
        seal_icon = (em.get(SkillType.PASSIVE_SEAL)
                     if skill.type != SkillType.PASSIVE_SEAL and skill.is_seal
                     else "")
        title = f'{skill.icon} {skill.name} · {type_icon}{seal_icon}'

        if (skill.type == SkillType.WEAPON
                or skill.type == SkillType.WEAPON_REFINED
           ):
            effective = SkillInfo.format_eff(skill)

            weapon_desc = f'Mt: {skill.might} Rng: {skill.range}{effective}'
        elif skill.type == SkillType.SPECIAL:
            weapon_desc = f'{em.get(SkillType.SPECIAL)} {skill.special_cd}'
        else: weapon_desc = None

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

        if skill.type != SkillType.WEAPON and skill.type != SkillType.WEAPON_REFINED:
            if skill.is_staff:
                restrictions = "_This skill can only be equipped by staff users._"
            else:
                if skill.restrict_from:
                    restrict_list = [str(em.get(type)) for type in skill.restrict_from]
                    restrictions = f'**Cannot use:** {"".join(restrict_list)}'
                else: restrictions = None
        else: restrictions = None

        sp = f'**SP:** {skill.sp}'

        learnable_count = (len(skill.learnable[1]) + len(skill.learnable[2])
                           + len(skill.learnable[3]) + len(skill.learnable[4])
                           + len(skill.learnable[5]))
        if (skill.type == SkillType.WEAPON and not skill.exclusive
                and ((skill.tier <= 2 and not skill.is_staff) or skill.tier <= 1)):
            learnable = 'Basic weapon available to most eligible heroes.'
        elif (skill.type == SkillType.ASSIST and skill.is_staff
              and skill.tier <= 1):
            learnable = 'Basic assist available to all staff users.'
        # elif reduce(lambda x, y: x + len(y), skill.learnable[1:], 0) > 20:
        elif learnable_count > 20:
            learnable = 'Over 20 heroes know this skill.'
        elif learnable_count == 0:
            learnable = 'None'
        else:
            learnable = '\n'.join([
                f'{count}{em.get(Rarity(count))}: '
                f'{", ".join([hero.short_name for hero in hero_list])}'
                for count, hero_list in enumerate(skill.learnable[1:], 1)
                if hero_list
            ])

        embed.clear_fields()
        if zoom_state:
            if skill.postreq:
                prf_postreq_count = reduce(
                    lambda x, y: x + 1 if y.exclusive else x,
                    skill.postreq,
                    0
                )
                # optimize note?
                postreq_list = (', '.join([
                    f'{postreq.icon} {postreq.name}'
                    for postreq in skill.postreq
                    if not postreq.exclusive
                ])
                if len(skill.postreq) - prf_postreq_count < 10
                else ', '.join([
                    f'{postreq.name}'
                    for postreq in skill.postreq
                    if not postreq.exclusive
                ]))

                prf_postreqs = (f' and {prf_postreq_count} Prf skills.'
                                if prf_postreq_count else '')
            else:
                postreq_list = 'None'
                prf_postreqs = ''

            postreqs = f'**Required for:** {postreq_list}{prf_postreqs}'

            cumul_sp = f'**Cumulative SP:** {skill.get_cumul_sp_recursive()}'
            if skill.evolves_from:
                evolve_src = (
                    f'**Evolves from:** '
                    f'{skill.evolves_from.icon} {skill.evolves_from.name}')
            else: evolve_src = None
        else:
            postreqs, cumul_sp, evolve_src = None, None, None

        description = '\n'.join(filter(None, [
            weapon_desc,
            skill.description,
            prereq,
            restrictions,
            sp,
            cumul_sp,
            '**Available from:**',
            learnable,
            evolve_src,
            postreqs,
        ]))

        embed.add_field(
            name = title,
            value = description,
            inline = False
        )

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
            if skill.refined_version and not skill.is_refined_variant:
                refined_skill = skill.refined_version
                refined_title = (f'Weapon Refinery\n{refined_skill.icon} '
                                 f'Refined {skill.name} · {type_icon}'
                                 )
                effective = SkillInfo.format_eff(refined_skill)
                refined_w_desc = (
                    f'Mt: {refined_skill.might} '
                    f'Rng: {refined_skill.range}{effective}'
                    if (refined_skill.type == SkillType.WEAPON
                        or refined_skill.type == SkillType.WEAPON_REFINED
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
                skill.refine_staff1,
                skill.refine_staff2,
                skill.refine_atk,
                skill.refine_spd,
                skill.refine_def,
                skill.refine_res
            )
            if zoom_state:
                generic_refines = '\n'.join([
                    f'{refine.icon}: {refine.description}'
                    for refine in skill_refines
                    if refine
                ])
            else:
                generic_refines = ', '.join([
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
            else: evolve_cost = ''

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
                evolution
            ]))
            embed.add_field(
                name = refined_title,
                value = refine_desc,
                inline = False
            )
        if (skill.type == SkillType.WEAPON
                or skill.type == SkillType.WEAPON_REFINED
                or (skill.type == SkillType.ASSIST and skill.is_staff)
        ):
            embed.set_thumbnail(url=f'https://raw.githubusercontent.com/imxtrabored/XanderBot/master/xanderbot/feh/data/skills/{skill.id}.png')
        else: embed.set_thumbnail(url=f'https://cdn.discordapp.com/emojis/{skill.icon.id}.png')

        if skill.weapon_type: embed.color = em.get_color(skill.weapon_type)
        else: embed.color = em.get_color(skill.type)
        return embed


    @staticmethod
    async def cmd(params):
        tokens = params.split(',')
        if not tokens:
            return 'No input detected!', None, None
        skill = UnitLib.get_skill(tokens[0])
        if not skill:
            return (
                f'Skill not found: {tokens[0]}.\n'
                'Note: To display information on the skills known by a hero '
                'by default, use the ``skills`` (with an s) command.',
                None, [None, False]
            )
        skill_embed = discord.Embed()
        zoom_state = False
        SkillInfo.format_skill(skill, skill_embed, zoom_state)
        return None, skill_embed, [skill, zoom_state]


    @staticmethod
    async def finalize(bot_reply):
        await bot_reply.add_reaction('🔍')
        await bot_reply.add_reaction('⬆')
        await bot_reply.add_reaction('⬇')


    @staticmethod
    async def react(reaction, bot_msg, embed, data):
        skill = data[0]
        if reaction.emoji == '🔍':
            data[1] = not data[1]
        elif reaction.emoji == '⬆':
            skill = skill.postreq[0] if skill.postreq else skill
        elif reaction.emoji == '⬇':
            skill = skill.prereq1 if skill.prereq1 else skill
        elif reaction.emoji == '👁':
            embed.set_author(name=str(skill.id))
        else: return None, None, False
        data[0] = skill
        embed = SkillInfo.format_skill(skill, embed, data[1])
        return None, embed, True
