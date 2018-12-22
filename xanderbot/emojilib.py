import sqlite3

from feh.hero import Color, UnitWeaponType, MoveType
from feh.hero import LegendElement, Stat
from feh.skill import SkillType, SkillWeaponGroup

class CompoundEmoji(tuple):
    __slots__ = ()
    def __str__(self):
        return ''.join([str(emoji) for emoji in self])

class EmojiLib(object):
    singleton = None

    @classmethod
    def initialize(cls, client, sqlite_instance = None):
        print('building emojilib...')

        con = sqlite3.connect("emojis.db", detect_types=sqlite3.PARSE_COLNAMES)
        cur = con.cursor()

        self = EmojiLib()

        self.emojis = dict()

        cur.execute("""SELECT * FROM emojis;""")
        for index in cur:
            if   index[0] == 'Stat_HP'        : self.emojis[Stat.HP ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Stat_Attack'    : self.emojis[Stat.ATK] = client.get_emoji(int(index[1]))
            elif index[0] == 'Stat_Speed'     : self.emojis[Stat.SPD] = client.get_emoji(int(index[1]))
            elif index[0] == 'Stat_Defense'   : self.emojis[Stat.DEF] = client.get_emoji(int(index[1]))
            elif index[0] == 'Stat_Resistance': self.emojis[Stat.RES] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Red_Sword'       : self.emojis[UnitWeaponType.R_SWORD ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Red_Tome'        : self.emojis[UnitWeaponType.R_TOME  ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Red_Bow'         : self.emojis[UnitWeaponType.R_BOW   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Red_Dagger'      : self.emojis[UnitWeaponType.R_DAGGER] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Red_Breath'      : self.emojis[UnitWeaponType.R_BREATH] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Blue_Lance'      : self.emojis[UnitWeaponType.B_LANCE ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Blue_Tome'       : self.emojis[UnitWeaponType.B_TOME  ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Blue_Bow'        : self.emojis[UnitWeaponType.B_BOW   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Blue_Dagger'     : self.emojis[UnitWeaponType.B_DAGGER] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Blue_Breath'     : self.emojis[UnitWeaponType.B_BREATH] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Green_Axe'       : self.emojis[UnitWeaponType.G_AXE   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Green_Tome'      : self.emojis[UnitWeaponType.G_TOME  ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Green_Bow'       : self.emojis[UnitWeaponType.G_BOW   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Green_Dagger'    : self.emojis[UnitWeaponType.G_DAGGER] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Green_Breath'    : self.emojis[UnitWeaponType.G_BREATH] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Colorless_Bow'   : self.emojis[UnitWeaponType.C_BOW   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Colorless_Dagger': self.emojis[UnitWeaponType.C_DAGGER] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Colorless_Staff' : self.emojis[UnitWeaponType.C_STAFF ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Weapon_Colorless_Breath': self.emojis[UnitWeaponType.C_BREATH] = client.get_emoji(int(index[1]))
            elif index[0] == 'Move_Infantry': self.emojis[MoveType.INFANTRY] = client.get_emoji(int(index[1]))
            elif index[0] == 'Move_Armor'   : self.emojis[MoveType.ARMOR   ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Move_Cavalry' : self.emojis[MoveType.CAVALRY ] = client.get_emoji(int(index[1]))
            elif index[0] == 'Move_Flier'   : self.emojis[MoveType.FLIER  ] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Element_Fire' : self.emojis[LegendElement.FIRE ] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Element_Water': self.emojis[LegendElement.WATER] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Element_Wind' : self.emojis[LegendElement.WIND ] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Element_Earth': self.emojis[LegendElement.EARTH] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Element_Light': self.emojis[LegendElement.LIGHT] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Element_Dark' : self.emojis[LegendElement.DARK ] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Element_Astra': self.emojis[LegendElement.ASTRA] = client.get_emoji(int(index[1]))
            elif index[0] == 'L_Element_Anima': self.emojis[LegendElement.ANIMA] = client.get_emoji(int(index[1]))

            else: self.emojis[index[0]] = client.get_emoji(int(index[1]))
        
        self.emojis[SkillWeaponGroup.R_SWORD ] = self.emojis[UnitWeaponType.R_SWORD]
        self.emojis[SkillWeaponGroup.R_TOME  ] = self.emojis[UnitWeaponType.R_TOME ]
        self.emojis[SkillWeaponGroup.B_LANCE ] = self.emojis[UnitWeaponType.B_LANCE]
        self.emojis[SkillWeaponGroup.B_TOME  ] = self.emojis[UnitWeaponType.B_TOME ]
        self.emojis[SkillWeaponGroup.G_AXE   ] = self.emojis[UnitWeaponType.G_AXE  ]
        self.emojis[SkillWeaponGroup.G_TOME  ] = self.emojis[UnitWeaponType.G_TOME ]
        self.emojis[SkillWeaponGroup.C_STAFF ] = self.emojis[UnitWeaponType.C_STAFF]

        self.emojis[SkillWeaponGroup.S_BREATH] = CompoundEmoji(
            [
                self.emojis[UnitWeaponType.R_BREATH],
                self.emojis[UnitWeaponType.B_BREATH],
                self.emojis[UnitWeaponType.G_BREATH],
                self.emojis[UnitWeaponType.C_BREATH]
            ])
        self.emojis[SkillWeaponGroup.S_BOW   ] = CompoundEmoji(
            [
                self.emojis[UnitWeaponType.R_BOW],
                self.emojis[UnitWeaponType.B_BOW],
                self.emojis[UnitWeaponType.G_BOW],
                self.emojis[UnitWeaponType.C_BOW]
            ])
        self.emojis[SkillWeaponGroup.S_DAGGER] = CompoundEmoji(
            [
                self.emojis[UnitWeaponType.R_DAGGER],
                self.emojis[UnitWeaponType.B_DAGGER],
                self.emojis[UnitWeaponType.G_DAGGER],
                self.emojis[UnitWeaponType.C_DAGGER]
            ])


        cls.singleton = self
        print('done.')

        return(self.emojis)

    @classmethod
    def get(cls, obj, *, single=False):
        if obj in cls.singleton.emojis:
           if not single: return cls.singleton.emojis[obj]
           if single and len(cls.singleton.emojis[obj]) > 1:
               pass

    @classmethod
    async def get_lib(cls):
        if cls.singleton == None:
            cls.initialize()
        return cls.singleton.emojis




