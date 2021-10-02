import tinydb
from _websocket import PATH

class StatisticsDatabase:

    def __init__(self):
        self.database = tinydb.TinyDB(PATH + '\\Recources\\statistics.db')
    
    def AddNewMobData(self, InstancesList, current_map):
        # {'id': int, 'x': int, 'y': int, 'type': int, 'vid': int}
        for instance in InstancesList:
            self.database.add(instance)


statDB = StatisticsDatabase()