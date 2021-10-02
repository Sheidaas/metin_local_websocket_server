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
    
    #Valid Type Numbers for mobs. Ignoring NPCs and Ores and other instances.
    VALID_TYPES = { 
            -1:'boss',
            0:'regular',
            2:'metin'
        }

    def __init__(self):
        self.database = TinyDB(PATH + '\\statistics.db')
        # setting short names for faster access
        self.loc = self.database.table('loc')
        self.mob = self.database.table('mob')
        self.map = self.database.table('map')
        if self.map.count(all) < 19: #current amount of maps, to check if filled, if yes skip. 
            self.PreFillDatabase()
        

    def PreFillDatabase(self):
        # pre-loading mob list into db - performance increase 
        mob_list = MetinMemoryObject.ReturnServerMobList()
        

        [self.mob.insert({'mob_id': mob.mob_id}) for mob in mob_list]

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
        
        [self.map.insert({'map_name':map_entity}) for map_entity in map_list]
    
    def AddNewMobData(self, InstancesList, current_map):
        # {'id': int, 'x': int, 'y': int, 'type': int, 'vid': int}
        
        for instance in InstancesList:
            #check if monster of any kind = Boss, Metin-Stone, regular mob 
            if instance.type in self.VALID_TYPES:

                mob_id = (self.mob.search(where('id')==instance.id))[0].doc_id #list should only return one item - thus accessing [0]
                map_id = (self.map.search(where('map_name')==current_map))[0].doc_id #again only one result
                #checking if exists to avoid duplicate locations - eventually to be removed, to create a "heat" map, where more mobs of this kind spawn.
                #this would (probably) decrease performance. To be checked if search uses less ressources than insert. 

                q = Query()
                if len(self.loc.search((q.mob_id==mob_id) & (q.map_id==map_id) & (q.x==instance.x) & (q.y==instance.y)))>1:

                    #insert into db
                    self.loc.insert({'mob_id':mob_id,'map_id':map_id, 'x':instance.x, 'y':instance.y})


    def ReturnMobLocation(self,mob_id:int): 
        # Returns: map{map_name:str, coord_map_list[{x,y},...]}
        # probably a lot of bug fixing necessary - dont kill me pls :D
        

        #getting database mob_id
        mob = (self.mob.search(where('id')==mob_id))[0].doc_id #only 1 item return, or broken db. 

        full_loc_list = self.loc.search(where('mob_id')==mob) #grabbing full location list for selected mob 
        
        #Sort by y first and then by x to have x and y sorted upwards
        full_loc_list = sorted(full_loc_list, key=lambda k:k['y'])
        full_loc_list = sorted(full_loc_list, key=lambda k:k['x']) 
        
        #Sort by map id last, to only have one map at a time.
        full_loc_list = sorted(full_loc_list, key=lambda k:k['map_id'])


        loc_list = {}

        ###
        # following values in calculation need to be adjusted, only an rough sketch without data. 
        # trying to figure out circles from available data. returning middle point of circle. 
         
        map_id=0
        loc_circle_x=[]
        loc_circle_y=[]

        loc_circle_centers=[]
        last_x=0
        last_y=0

        while len(full_loc_list>0):
            loc = full_loc_list.pop(0)      #reduce location lists one by one
    
            #select only close mob ranges next to each other. Further away mobs are new spawning circles.
            if loc['x']-last_x<100 and loc['y']-last_y<100: #TODO: Figure out optimal range (currently 100)
                loc_circle_x.append(loc['x'])
                loc_circle_y.append(loc['y'])
            else:
                loc_circle_centers.append(self.ReturnCircleCenter(loc_circle_x, loc_circle_y))
                log_circle_x=[]
                loc_circle_y=[]
                loc_circle_x.append(loc['x'])
                loc_circle_y.append(loc['y'])


            if loc['map_id']!=map_id:       #check if map changes
                if map_id==0:               #ignore first change from default value to read map
                    map_id=loc['map_id']
                else:
                    loc_circle_centers.append(self.ReturnCircleCenter(loc_circle_x,loc_circle_y)) #append one last circle
                    #get map name
                    map_name = self.map.get(doc_id=map_id)
                    loc_list[map_name]=loc_circle_centers
                    last_x=0
                    last_y=0
                    log_circle_x=[]
                    loc_circle_y=[]
                    loc_circle_centers=[]

        #One last time for final Circle and map after full location list is empty 

        loc_circle_centers.append(self.ReturnCircleCenter(loc_circle_x,loc_circle_y)) #append one last circle
        #get map name
        map_name = self.map.get(doc_id=map_id)
        loc_list[map_name]=loc_circle_centers

        return loc_list 
    
    test1 = [{'id':1,'map':1,'x':10,'y':10}]

    def ReturnCircleCenter(list_x, list_y):
        return {'x':(sum(list_x)/len(list_x)),'y':(sum(list_y)/len(list_y))}

statDB = StatisticsDatabase()
