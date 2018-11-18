import sqlite3
from Hero import Hero

class UnitLib(object):
    '''Library of units, loaded into memory'''

    async def initialize(self, sqliteInstance):
        self.unitList = []
        self.unitList.append(Hero.create('null'))
        self.nameTable = dict()
        self.nameTable['null'] = self.unitList[0]
