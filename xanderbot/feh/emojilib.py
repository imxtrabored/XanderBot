import sqlite3

from feh.hero import Color, UnitWeaponType, MoveType
from feh.hero import LegendElement, LegendStat, Stat, Rarity
from feh.skill import SkillType, SkillWeaponGroup

class CompoundEmoji(tuple):
    __slots__ = ()
    def __str__(self):
        return ''.join([str(emoji) for emoji in self])

class EmojiLib(object):
    singleton = None
    restrict_emojis = ()

    @classmethod
    def initialize(cls, client):
        print('building emojilib...')

        con = sqlite3.connect("feh/emojis.db", detect_types=sqlite3.PARSE_COLNAMES)
        cur = con.cursor()

        self = EmojiLib()
        cls.singleton = self


        self.emojis = dict()

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

            else: self.emojis[index[0]] = client.get_emoji(int(index[1]))
        
        self.emojis[SkillWeaponGroup.R_SWORD] = self.emojis[UnitWeaponType.R_SWORD]
        self.emojis[SkillWeaponGroup.R_TOME ] = self.emojis[UnitWeaponType.R_TOME ]
        self.emojis[SkillWeaponGroup.B_LANCE] = self.emojis[UnitWeaponType.B_LANCE]
        self.emojis[SkillWeaponGroup.B_TOME ] = self.emojis[UnitWeaponType.B_TOME ]
        self.emojis[SkillWeaponGroup.G_AXE  ] = self.emojis[UnitWeaponType.G_AXE  ]
        self.emojis[SkillWeaponGroup.G_TOME ] = self.emojis[UnitWeaponType.G_TOME ]
        self.emojis[SkillWeaponGroup.C_STAFF] = self.emojis[UnitWeaponType.C_STAFF]

        self.emojis[SkillWeaponGroup.S_BREATH] = CompoundEmoji((
            self.emojis[UnitWeaponType.R_BREATH],
            self.emojis[UnitWeaponType.B_BREATH],
            self.emojis[UnitWeaponType.G_BREATH],
            self.emojis[UnitWeaponType.C_BREATH],
        ))
        self.emojis[SkillWeaponGroup.S_BOW] = CompoundEmoji((
            self.emojis[UnitWeaponType.R_BOW],
            self.emojis[UnitWeaponType.B_BOW],
            self.emojis[UnitWeaponType.G_BOW],
            self.emojis[UnitWeaponType.C_BOW],
        ))
        self.emojis[SkillWeaponGroup.S_DAGGER] = CompoundEmoji((
            self.emojis[UnitWeaponType.R_DAGGER],
            self.emojis[UnitWeaponType.B_DAGGER],
            self.emojis[UnitWeaponType.G_DAGGER],
            self.emojis[UnitWeaponType.C_DAGGER],
        ))
        self.emojis[SkillWeaponGroup.S_BEAST] = CompoundEmoji((
            self.emojis[UnitWeaponType.R_BEAST],
            self.emojis[UnitWeaponType.B_BEAST],
            self.emojis[UnitWeaponType.G_BEAST],
            self.emojis[UnitWeaponType.C_BEAST],
        ))

        EmojiLib.restrict_emojis = (
            str(self.emojis[MoveType.INFANTRY      ]),
            str(self.emojis[MoveType.ARMOR         ]),
            str(self.emojis[MoveType.CAVALRY       ]),
            str(self.emojis[MoveType.FLIER         ]),
            str(self.emojis[UnitWeaponType.R_SWORD ]),
            str(self.emojis[UnitWeaponType.R_TOME  ]),
            str(self.emojis[UnitWeaponType.R_BOW   ]),
            str(self.emojis[UnitWeaponType.R_DAGGER]),
            str(self.emojis[UnitWeaponType.R_BREATH]),
            str(self.emojis[UnitWeaponType.R_BEAST ]),
            str(self.emojis[UnitWeaponType.B_LANCE ]),
            str(self.emojis[UnitWeaponType.B_TOME  ]),
            str(self.emojis[UnitWeaponType.B_BOW   ]),
            str(self.emojis[UnitWeaponType.B_DAGGER]),
            str(self.emojis[UnitWeaponType.B_BREATH]),
            str(self.emojis[UnitWeaponType.B_BEAST ]),
            str(self.emojis[UnitWeaponType.G_AXE   ]),
            str(self.emojis[UnitWeaponType.G_TOME  ]),
            str(self.emojis[UnitWeaponType.G_BOW   ]),
            str(self.emojis[UnitWeaponType.G_DAGGER]),
            str(self.emojis[UnitWeaponType.G_BREATH]),
            str(self.emojis[UnitWeaponType.G_BEAST ]),
            str(self.emojis[UnitWeaponType.C_BOW   ]),
            str(self.emojis[UnitWeaponType.C_DAGGER]),
            str(self.emojis[UnitWeaponType.C_STAFF ]),
            str(self.emojis[UnitWeaponType.C_BREATH]),
            str(self.emojis[UnitWeaponType.C_BEAST ]),
        )

        print('done.')
        con.close()
        return self.emojis



    @classmethod
    def get(cls, obj, *, single=False):
        if obj in cls.singleton.emojis:
            if not single: return cls.singleton.emojis.get(obj)
            if single and len(cls.singleton.emojis[obj]) > 1:
                return cls.singleton.emojis[obj][-1]



    @classmethod
    async def get_lib(cls):
        if cls.singleton is None:
            pass
        return cls.singleton.emojis

