from tinydb import TinyDB,Query
from tinydb import queries
from tinydb.queries import where
from MetinMemoryObject import MetinMemoryObject
from _websocket import PATH

class StatisticsDatabase:


    # creating for later class-wide-usage, defining in init
    loc = None
    mob = None
    map = None

    def __init__(self):
        self.database = TinyDB(PATH + '\\statistics.db')
        # setting short names for faster access
        self.loc = self.database.table('loc')
        self.mob = self.database.table('mob')
        self.map = self.database.table('map')
        # pre-loading mob list into db - performance increase 
        mob_list = MetinMemoryObject.ReturnServerMobList
        
        for mob_entity in mob_list:
            self.mob.insert({'mob_id':mob_entity.mob_id})

        # pre-loading map list into db - performance increase 
        map_list = ["map_a2",
        "map_n_snowm_01",
        "metin2_map_b1",
        "metin2_map_b3",
        "metin2_map_c1",
        "metin2_map_c3",
        "metin2_map_devilsCatacomb",
        "metin2_map_deviltower1",
        "metin2_map_guild_02",
        "metin2_map_milgyo",
        "metin2_map_monkeydungeon_03",
        "metin2_map_monkeydungeon",
        "metin2_map_n_desert_01",
        "metin2_map_n_flame_01",
        "metin2_map_privateshop",
        "metin2_map_spiderdungeon_02",
        "metin2_map_spiderdungeon",
        "metin2_map_trent02",
        "metin2_map_trent"]
        
        for map_entity in mob_list:
            self.map.insert({'map_name':map_entity})

        
    
    def AddNewMobData(self, InstancesList, current_map):
        # {'id': int, 'x': int, 'y': int, 'type': int, 'vid': int}
        valid_types = [-1,0,2]
        for instance in InstancesList:
            #check if monster of any kind = Boss, Metin-Stone, regular mob 
            if instance.type in valid_types:

                mob_id = (self.mob.search(where('id')==instance.id))[0].doc_id #list should only return one item - thus accessing [0]
                map_id = (self.map.search(where('map_name')==current_map))[0].doc_id #again only one result
                #checking if exists to avoid duplicate locations - eventually to be removed, to create a "heat" map, where more mobs of this kind spawn.
                #this would (probably) decrease performance. To be checked if search uses less ressources than insert. 

                q = Query()
                if self.loc.search((q.mob_id==mob_id) & (q.map_id==map_id) & (q.x==instance.x) & (q.y==instance.y)).__len__>1:

                    #insert into db
                    self.loc.insert({'mob_id':mob_id,'map_id':map_id, 'x':instance.x, 'y':instance.y})
        


statDB = StatisticsDatabase()