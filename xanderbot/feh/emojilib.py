import sqlite3

from discord import Color

from feh.currency import Dragonflower
from feh.hero import (
    UnitColor, UnitWeaponType, MoveType, LegendElement, LegendStat, Stat,
    Rarity, SummonerSupport
)
from feh.interface import DragonflowerInc, RarityInc
from feh.skill import SkillType, SkillWeaponGroup


class EmojiLib(object):
    singleton = None
    restrict_emojis = ()
    emojis = dict()
    colors = {
        SkillType.NONE           : Color.from_rgb(120,82,163) ,
        SkillType.WEAPON         : Color.from_rgb(120,82,163) ,
        SkillType.ASSIST         : Color.from_rgb(0,239,199)  ,
        SkillType.SPECIAL        : Color.from_rgb(255,137,255),
        SkillType.PASSIVE_A      : Color.from_rgb(255,76,106) ,
        SkillType.PASSIVE_B      : Color.from_rgb(0,148,222)  ,
        SkillType.PASSIVE_C      : Color.from_rgb(1,201,70)   ,
        SkillType.PASSIVE_SEAL   : Color.from_rgb(255,238,51) ,
        SkillType.WEAPON_REFINED : Color.from_rgb(120,82,163) ,
        SkillType.REFINE         : Color.from_rgb(120,82,163) ,
        SkillWeaponGroup.NONE    : Color.from_rgb(95,111,118) ,
        SkillWeaponGroup.R_SWORD : Color.from_rgb(228,34,67)  ,
        SkillWeaponGroup.R_TOME  : Color.from_rgb(228,34,67)  ,
        SkillWeaponGroup.S_BREATH: Color.from_rgb(95,111,118) ,
        SkillWeaponGroup.B_LANCE : Color.from_rgb(40,101,223) ,
        SkillWeaponGroup.B_TOME  : Color.from_rgb(40,101,223) ,
        SkillWeaponGroup.G_AXE   : Color.from_rgb(10,172,37)  ,
        SkillWeaponGroup.G_TOME  : Color.from_rgb(10,172,37)  ,
        SkillWeaponGroup.S_BOW   : Color.from_rgb(95,111,118) ,
        SkillWeaponGroup.S_DAGGER: Color.from_rgb(95,111,118) ,
        SkillWeaponGroup.C_STAFF : Color.from_rgb(95,111,118) ,
        SkillWeaponGroup.S_BEAST : Color.from_rgb(95,111,118) ,
        SkillWeaponGroup.S_TOME  : Color.from_rgb(120,82,163) ,
        UnitColor.NONE           : Color.from_rgb(95,111,118) ,
        UnitColor.RED            : Color.from_rgb(228,34,67)  ,
        UnitColor.BLUE           : Color.from_rgb(40,101,223) ,
        UnitColor.GREEN          : Color.from_rgb(10,172,37)  ,
        UnitColor.COLORLESS      : Color.from_rgb(95,111,118) ,
        None                     : Color.from_rgb(120,82,163) ,
    }

    @classmethod
    def initialize(cls, client):
        print('building emojilib...')
        con = sqlite3.connect("feh/emojis.db")
        cur = con.cursor()
        self = EmojiLib()
        cls.singleton = self
        self.emojis.clear()
        cur.execute("""SELECT name, id FROM emojis;""")
        for index in cur:
            # ok look this is (probably) still better than storing python objects in db
            if   index[0] == 'Stat_HP' : self.emojis[Stat.HP ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Stat_Atk': self.emojis[Stat.ATK] = client.get_emoji(int(index[1]))
            elif index[0] == 'Stat_Spd': self.emojis[Stat.SPD] = client.get_emoji(int(index[1]))
            elif index[0] == 'Stat_Def': self.emojis[Stat.DEF] = client.get_emoji(int(index[1]))
            elif index[0] == 'Stat_Res': self.emojis[Stat.RES] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_R_Sword' : self.emojis[UnitWeaponType.R_SWORD ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_R_Tome'  : self.emojis[UnitWeaponType.R_TOME  ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_R_Bow'   : self.emojis[UnitWeaponType.R_BOW   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_R_Dagger': self.emojis[UnitWeaponType.R_DAGGER] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_R_Breath': self.emojis[UnitWeaponType.R_BREATH] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_B_Lance' : self.emojis[UnitWeaponType.B_LANCE ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_B_Tome'  : self.emojis[UnitWeaponType.B_TOME  ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_B_Bow'   : self.emojis[UnitWeaponType.B_BOW   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_B_Dagger': self.emojis[UnitWeaponType.B_DAGGER] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_B_Breath': self.emojis[UnitWeaponType.B_BREATH] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_G_Axe'   : self.emojis[UnitWeaponType.G_AXE   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_G_Tome'  : self.emojis[UnitWeaponType.G_TOME  ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_G_Bow'   : self.emojis[UnitWeaponType.G_BOW   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_G_Dagger': self.emojis[UnitWeaponType.G_DAGGER] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_G_Breath': self.emojis[UnitWeaponType.G_BREATH] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_C_Bow'   : self.emojis[UnitWeaponType.C_BOW   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_C_Dagger': self.emojis[UnitWeaponType.C_DAGGER] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_C_Staff' : self.emojis[UnitWeaponType.C_STAFF ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_C_Breath': self.emojis[UnitWeaponType.C_BREATH] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_R_Beast' : self.emojis[UnitWeaponType.R_BEAST ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_B_Beast' : self.emojis[UnitWeaponType.B_BEAST ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_G_Beast' : self.emojis[UnitWeaponType.G_BEAST ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Wp_C_Beast' : self.emojis[UnitWeaponType.C_BEAST ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Move_Infantry': self.emojis[MoveType.INFANTRY] = client.get_emoji(int(index[1]))
            elif index[0] == 'Move_Armor'   : self.emojis[MoveType.ARMOR   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Move_Cavalry' : self.emojis[MoveType.CAVALRY ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Move_Flier'   : self.emojis[MoveType.FLIER   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Element_Fire' : self.emojis[LegendElement.FIRE ] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Element_Water': self.emojis[LegendElement.WATER] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Element_Wind' : self.emojis[LegendElement.WIND ] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Element_Earth': self.emojis[LegendElement.EARTH] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Element_Light': self.emojis[LegendElement.LIGHT] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Element_Dark' : self.emojis[LegendElement.DARK ] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Element_Astra': self.emojis[LegendElement.ASTRA] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Element_Anima': self.emojis[LegendElement.ANIMA] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Stat_Atk': self.emojis[LegendStat.ATK] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Stat_Spd': self.emojis[LegendStat.SPD] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Stat_Def': self.emojis[LegendStat.DEF] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Stat_Res': self.emojis[LegendStat.RES] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Stat_Duel':
                self.emojis[LegendStat.DUEL] = client.get_emoji(int(index[1]))
                self.emojis[LegendStat.DUEL2] = client.get_emoji(int(index[1]))
            elif index[0] == 'Skill_Weapon' : self.emojis[SkillType.WEAPON ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Skill_Assist' : self.emojis[SkillType.ASSIST ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Skill_Special': self.emojis[SkillType.SPECIAL] = client.get_emoji(int(index[1]))
            elif index[0] == 'Skill_A': self.emojis[SkillType.PASSIVE_A] = client.get_emoji(int(index[1]))
            elif index[0] == 'Skill_B': self.emojis[SkillType.PASSIVE_B] = client.get_emoji(int(index[1]))
            elif index[0] == 'Skill_C': self.emojis[SkillType.PASSIVE_C] = client.get_emoji(int(index[1]))
            elif index[0] == 'Skill_S': self.emojis[SkillType.PASSIVE_SEAL] = client.get_emoji(int(index[1]))
            elif index[0] == 'Rarity_1': self.emojis[Rarity.ONE  ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Rarity_2': self.emojis[Rarity.TWO  ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Rarity_3': self.emojis[Rarity.THREE] = client.get_emoji(int(index[1]))
            elif index[0] == 'Rarity_4': self.emojis[Rarity.FOUR ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Rarity_5': self.emojis[Rarity.FIVE ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Currency_Refining_Stone':
                self.emojis[Rarity.STONE] = client.get_emoji(int(index[1]))
                self.emojis['Currency_Refining_Stone'] = client.get_emoji(int(index[1]))
            elif index[0] == 'Currency_Divine_Dew':
                self.emojis[Rarity.DEW] = client.get_emoji(int(index[1]))
                self.emojis['Currency_Divine_Dew'] = client.get_emoji(int(index[1]))
            elif index[0] == 'Df_Inf': self.emojis[Dragonflower.INFANTRY] = client.get_emoji(int(index[1]))
            elif index[0] == 'Df_Arm': self.emojis[Dragonflower.ARMOR   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Df_Cav': self.emojis[Dragonflower.CAVALRY ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Df_Fly': self.emojis[Dragonflower.FLIER   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'SummSuppC': self.emojis[SummonerSupport.C] = client.get_emoji(int(index[1]))
            elif index[0] == 'SummSuppB': self.emojis[SummonerSupport.B] = client.get_emoji(int(index[1]))
            elif index[0] == 'SummSuppA': self.emojis[SummonerSupport.A] = client.get_emoji(int(index[1]))
            elif index[0] == 'SummSuppS': self.emojis[SummonerSupport.S] = client.get_emoji(int(index[1]))
            elif index[0] == 'RarityUp'  : self.emojis[RarityInc.UP] = client.get_emoji(int(index[1]))
            elif index[0] == 'RarityDown': self.emojis[RarityInc.DOWN] = client.get_emoji(int(index[1]))
            elif index[0] == 'DfUpInf': self.emojis[DragonflowerInc.INFANTRY] = client.get_emoji(int(index[1]))
            elif index[0] == 'DfUpArm': self.emojis[DragonflowerInc.ARMOR   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'DfUpCav': self.emojis[DragonflowerInc.CAVALRY ] = client.get_emoji(int(index[1]))
            elif index[0] == 'DfUpFly': self.emojis[DragonflowerInc.FLIER   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'DfDown' : self.emojis[DragonflowerInc.DOWN    ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Empty' : self.emojis[None] = client.get_emoji(int(index[1]))
            else: self.emojis[index[0]] = client.get_emoji(int(index[1]))
        con.close()
        self.emojis[SummonerSupport.NONE] = ''
        print('done.')
        return self.emojis

    @classmethod
    def get(cls, obj, *, single=False):
        if obj in cls.singleton.emojis:
            if not single:
                return cls.singleton.emojis.get(obj)
            if single and len(cls.singleton.emojis[obj]) > 1:
                return cls.singleton.emojis[obj][-1]
        return cls.singleton.emojis[None]

    @classmethod
    def get_color(cls, obj):
        return cls.colors.get(obj)

    @classmethod
    async def get_lib(cls):
        if cls.singleton is None:
            pass
        return cls.singleton.emojis
