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
        SkillWeaponGroup.S_TOME  : Color.from_rgb(95,111,118) ,
        SkillWeaponGroup.C_TOME  : Color.from_rgb(95,111,118) ,
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

    emoji_index = {
        'Stat_HP' : Stat.HP ,
        'Stat_Atk': Stat.ATK,
        'Stat_Spd': Stat.SPD,
        'Stat_Def': Stat.DEF,
        'Stat_Res': Stat.RES,
        'Wp_R_Sword' : UnitWeaponType.R_SWORD ,
        'Wp_R_Tome'  : UnitWeaponType.R_TOME  ,
        'Wp_R_Bow'   : UnitWeaponType.R_BOW   ,
        'Wp_R_Dagger': UnitWeaponType.R_DAGGER,
        'Wp_R_Breath': UnitWeaponType.R_BREATH,
        'Wp_B_Lance' : UnitWeaponType.B_LANCE ,
        'Wp_B_Tome'  : UnitWeaponType.B_TOME  ,
        'Wp_B_Bow'   : UnitWeaponType.B_BOW   ,
        'Wp_B_Dagger': UnitWeaponType.B_DAGGER,
        'Wp_B_Breath': UnitWeaponType.B_BREATH,
        'Wp_G_Axe'   : UnitWeaponType.G_AXE   ,
        'Wp_G_Tome'  : UnitWeaponType.G_TOME  ,
        'Wp_G_Bow'   : UnitWeaponType.G_BOW   ,
        'Wp_G_Dagger': UnitWeaponType.G_DAGGER,
        'Wp_G_Breath': UnitWeaponType.G_BREATH,
        'Wp_C_Bow'   : UnitWeaponType.C_BOW   ,
        'Wp_C_Dagger': UnitWeaponType.C_DAGGER,
        'Wp_C_Tome'  : UnitWeaponType.C_TOME  ,
        'Wp_C_Staff' : UnitWeaponType.C_STAFF ,
        'Wp_C_Breath': UnitWeaponType.C_BREATH,
        'Wp_R_Beast' : UnitWeaponType.R_BEAST ,
        'Wp_B_Beast' : UnitWeaponType.B_BEAST ,
        'Wp_G_Beast' : UnitWeaponType.G_BEAST ,
        'Wp_C_Beast' : UnitWeaponType.C_BEAST ,
        'Move_Infantry': MoveType.INFANTRY,
        'Move_Armor'   : MoveType.ARMOR   ,
        'Move_Cavalry' : MoveType.CAVALRY ,
        'Move_Flier'   : MoveType.FLIER   ,
        'L_Element_Fire' : LegendElement.FIRE ,
        'L_Element_Water': LegendElement.WATER,
        'L_Element_Wind' : LegendElement.WIND ,
        'L_Element_Earth': LegendElement.EARTH,
        'L_Element_Light': LegendElement.LIGHT,
        'L_Element_Dark' : LegendElement.DARK ,
        'L_Element_Astra': LegendElement.ASTRA,
        'L_Element_Anima': LegendElement.ANIMA,
        'L_Stat_Atk': LegendStat.ATK,
        'L_Stat_Spd': LegendStat.SPD,
        'L_Stat_Def': LegendStat.DEF,
        'L_Stat_Res': LegendStat.RES,
        'L_Stat_Duel' : LegendStat.DUEL ,
        'L_Stat_Duel2': LegendStat.DUEL2,
        'Skill_Weapon' : SkillType.WEAPON ,
        'Skill_Assist' : SkillType.ASSIST ,
        'Skill_Special': SkillType.SPECIAL,
        'Skill_A': SkillType.PASSIVE_A,
        'Skill_B': SkillType.PASSIVE_B,
        'Skill_C': SkillType.PASSIVE_C,
        'Skill_S': SkillType.PASSIVE_SEAL,
        'Rarity_1': Rarity.ONE  ,
        'Rarity_2': Rarity.TWO  ,
        'Rarity_3': Rarity.THREE,
        'Rarity_4': Rarity.FOUR ,
        'Rarity_5': Rarity.FIVE ,
        'Rarity_Stone': Rarity.STONE,
        'Rarity_Dew'  : Rarity.DEW  ,
        'Currency_Refining_Stone' : 'Currency_Refining_Stone',
        'Currency_Divine_Dew': 'Currency_Divine_Dew',
        'Df_Inf': Dragonflower.INFANTRY,
        'Df_Arm': Dragonflower.ARMOR   ,
        'Df_Cav': Dragonflower.CAVALRY ,
        'Df_Fly': Dragonflower.FLIER   ,
        'SummSuppC': SummonerSupport.C,
        'SummSuppB': SummonerSupport.B,
        'SummSuppA': SummonerSupport.A,
        'SummSuppS': SummonerSupport.S,
        'RarityUp'  : RarityInc.UP,
        'RarityDown': RarityInc.DOWN,
        'DfUpInf': DragonflowerInc.INFANTRY,
        'DfUpArm': DragonflowerInc.ARMOR   ,
        'DfUpCav': DragonflowerInc.CAVALRY ,
        'DfUpFly': DragonflowerInc.FLIER   ,
        'DfDown' : DragonflowerInc.DOWN    ,
        'Empty': None,
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
            # alright i improved this a bit
            self.emojis[emoji_index.get(index[0], index[0])] = (
                client.get_emoji(int(index[1])))
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
