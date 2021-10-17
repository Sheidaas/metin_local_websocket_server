from . import FileLoader
instance_valid_keys = {'id': int, 'x': int, 'y': int, 'type': int, 'vid': int}
data_valid_keys = ['message', 'action']

ACTIONS = {'SET_VIDS': 'set_vids',
           'SET_CHARACTER_STATUS': 'set_character_status',
           'SET_HACK_STATUS': 'set_hack_status',
           'SET_INVENTORY_STATUS': 'set_inventory_status',
           'SET_PICKUP_FILTER': 'set_pickup_filter',
           }

class MetinMemoryObject:

    def __init__(self):
        self.encoding = ''
        self.character_status = {
            'Server': '',
            'CurrentChannel': 0,
            'Position': [0, 0],
            'CurrentMap': 'None',
            'FirstEmpireMap': 'None',
            'SecondEmpireMap': 'None',
            'Name': 'None',
            'Experience': 0,
            'MaxExperience': 0,
            'Money': 0,
            'MovingSpeed': 0,
            'GUILD_ID': 0,
            'GuildName': 'None',
            'DefBonus': 0,
            'AttBonus': 0,
            'AttPower': 0,
            'AttSpeed': 0, 
            'Stamina': 0,
            'MaxStamina': 0,
            'HP': 0,
            'MaxHP': 0,
            'RecoveryHP': 0,
            'RecoverySP': 0,
            'SP': 0,
            'MaxSP': 0,
            'MP': 0,
            'MaxMP': 0,
            'Level': 0,
            'Vitality': 0,
            'Inteligence': 0,
            'Strength': 0,
            'Dexterity': 0,
            'IsMountingHorse': 0,
            'DefGrade': 0,
            'Skills': {}}
        self.hack_options = {
            'WaitHack': {},
            'SkillBot': {},
            'FarmBot': {},
            'Settings': {},
            'ActionBot': {},
            'ChannelSwitcher': {}}
        self.InstancesList = []
        self.Equipment = {}
        self.Inventory = []
        self.PickupFilter = []

    def OnReceiveInformation(self, received_information):
        from .StatisticsDatabase import statDB
        #print(received_information)
        if not self.ValidateReceivedInformation(received_information):
            print('cleaned_information is empty')
            return False
        else: #if not empty reformat message to UTF8 
            received_information = self.convertToUTF8(received_information,self.encoding)

        if received_information['action'] == ACTIONS['SET_VIDS']:
            self.InstancesList = [None] * len(received_information['data'])
            for instance in range(len(received_information['data'])):
                self.InstancesList[instance] = received_information['data'][instance]

            statDB.AddNewMobData(self.InstancesList, self.character_status['CurrentMap'])
            #print(statDB.ReturnMobLocation(101))
            return True

        if received_information['action'] == ACTIONS['SET_CHARACTER_STATUS']:
            for status_key in received_information['data'].keys():
                self.character_status[status_key] = received_information['data'][status_key]
            return True

        if received_information['action'] == ACTIONS['SET_HACK_STATUS']:
            for hack_option in received_information['data'].keys():
                self.hack_options[hack_option] = received_information['data'][hack_option]
            return True
        
        if received_information['action'] == ACTIONS['SET_INVENTORY_STATUS']:
            self.Inventory = received_information['data']['Inventory']
            self.Equipment = received_information['data']['Equipment']
            #print(self.Inventory)
            return True

        if received_information['action'] == ACTIONS['SET_PICKUP_FILTER']:
            #print(received_information)
            self.PickupFilter = received_information['data']
            return True

    def ValidateReceivedInformation(self, received_information):
        #print(received_information)
        if received_information['action'] == 'set_vids':
            if not type(received_information['data']) == list:
                print('Data[message] is not a list!')
                return False

            if not received_information['data']:
                print('Data[message] is empty')
                return False

            for instance in received_information['data']:
                if not type(instance) == dict:
                    return False

                for instance_key in instance.keys():
                    if instance_key not in instance_valid_keys.keys():
                        print(instance, ' is not in ' + str(instance_valid_keys.keys()))
                        return False

                    if not isinstance(type(instance[instance_key]), type(instance_valid_keys[instance_key])):
                        print('mob has wrong data')
                        return False

        elif received_information['action'] == 'set_character_status':
            #print(type(received_information['data']))
            if not type(received_information['data']) == dict:
                print('data is not dict')
                return False
            valid_keys = self.character_status.keys()
            for status_key in received_information['data'].keys():
                if status_key not in valid_keys:
                    print(status_key, ' is not in ', valid_keys)
                    return False

                if not type(received_information['data'][status_key]) == type(self.character_status[status_key]):
                    print(type(received_information['data'][status_key]), type(self.character_status[status_key]))
                    print(status_key, ' have different types ', valid_keys)
                    return False
               
                if type(received_information['data'][status_key]) == tuple:
                    if not len(self.character_status[status_key]) == len(received_information['data'][status_key]):
                        print('Tuples have different lengths')
                        return False
                    
                    for tuple_index in range(len(received_information['data'][status_key])):
                        if not type(received_information['data'][status_key][tuple_index]) == type(self.character_status[status_key][tuple_index]):
                            print('tuples have different types')
                            return False

        elif received_information['action'] == 'set_hack_status':
            if not type(received_information['data']) == dict:
                print('data is not dict')
                return False

            for message_key in received_information['data'].keys():
                if message_key not in self.hack_options.keys():
                    print(message_key, ' is not in hack options')
                    return False
            
            

        return True

    def ReturnServerItemList(self, PATH):
        return FileLoader.load_item_list(PATH)
    
    def ReturnServerMobList(self, PATH):
        return FileLoader.load_mob_list(PATH)

    #####
    # Converting to UTF 8 Methods
    #ignoring ints, floats and other numbers in this conversion. only texts of values relevant.

    def convertToUTF8(self,data,enc='1252'):
        if (isinstance(data,dict)):
            return self.dictToUtf8(data,enc)
        elif (isinstance(data,tuple)):
            return self.tupleToUtf8(data,enc)
        elif (isinstance(data,list)):
            return self.listToUtf8(data,enc)
        elif (isinstance(data,str)):
            return self.stringToUTF8(data,enc)
        return data

    def dictToUtf8(self,dic,enc):
        for key in dic:
            if (isinstance(dic[key],dict)):
                dic[key] = self.dictToUtf8(dic[key],enc)
            elif (isinstance(dic[key],tuple)):
                dic[key] = self.tupleToUtf8(dic[key],enc)
            elif (isinstance(dic[key],list)):
                dic[key] = self.listToUtf8(dic[key],enc)
            elif (isinstance(dic[key],str)):
                dic[key] = self.stringToUTF8(dic[key],enc)
        return dic

    def tupleToUtf8(self,tupl,enc):
        tupl_new=[]
        for item in tupl:
            if(isinstance(item,str)):
                item=self.stringToUTF8(item,enc)
            elif(isinstance(item,dict)):
                item=self.dictToUtf8(item,enc)
            elif(isinstance(item,list)):
                item=self.listToUtf8(item,enc)
            elif(isinstance(item,tuple)):
                item=self.tupleToUtf8(item,enc)
            tupl_new.append(item)
        return tuple(tupl_new)

    def listToUtf8(self,lis,enc):
        lis_new=[]
        for item in lis:
            if(isinstance(item,str)):
                item=self.stringToUTF8(item,enc)
            elif(isinstance(item,dict)):
                item=self.dictToUtf8(item,enc)
            elif(isinstance(item,list)):
                item=self.listToUtf8(item,enc)
            elif(isinstance(item,tuple)):
                item=self.tupleToUtf8(item,enc)
            lis_new.append(item)
        return lis_new
        

    def stringToUTF8(s,enc): 
        s=s.decode('cp'+enc)   
        s=s.encode('utf-8')
        return s

    # End UTF8 Conversion Functions
    ######
