from tinydb import TinyDB
from tinydb.queries import where
from _websocket import PATH
from math import sqrt
from pathlib import Path as OSPath

VALID_TYPES = {
    'BOSS': -1,
    'MONSTER': 0,
    'METIN': 2
}
class StatisticsDatabase:

    #Valid Type Numbers for mobs. Ignoring NPCs and Ores and other instances.


    def __init__(self):
        self.database = TinyDB(OSPath(PATH + '/Resources/statistics.db'))
        # setting short names for faster access
        self.mobs = self.database.table('mobs')

    def AddNewMobData(self, InstancesList, current_map):
        # {'id': int, 'x': int, 'y': int, 'type': int, 'vid': int}
        parsed_mobs = []
        for instance in InstancesList:
            if instance['type'] in [VALID_TYPES[value] for value in VALID_TYPES.keys()]:
                parsed_mobs.append({'id': instance['id'], 'map': current_map, 'location': [instance['x'], instance['y']]})
        self.mobs.insert_multiple(parsed_mobs)

    def ReturnMobLocation(self, mob_id: int):
        # Returns: map{map_name:str, coord_map_list[{x,y},...]}
        # probably a lot of bug fixing necessary - dont kill me pls :D

        mobs = self.mobs.search(where('id') == mob_id) #grabbing full location list for selected mob
        if not mobs:
            return None

        maps_with_locations = {}
        for mob in mobs:
            if mob['map'] in maps_with_locations.keys():
                maps_with_locations[mob['map']].append(mob['location'])
            else:
                maps_with_locations[mob['map']] = [mob['location']]

        for map_name in maps_with_locations.keys():
            to_close_points = []
            points = []
            for location in maps_with_locations[map_name]:
                if location in to_close_points or location in points: continue
                [to_close_points.append(_location)
                 if sqrt((location[0] - _location[0]) ** 2 + (location[1] - _location[1]) ** 2) < 2000 and
                    _location not in points and _location != location else _location for _location in maps_with_locations[map_name]]
                points.append(location)
            maps_with_locations[map_name] = points

        return maps_with_locations

statDB = StatisticsDatabase()
