from . import FileLoader
instance_valid_keys = {'id': int, 'x': int, 'y': int, 'type': int, 'vid': int, 'name': str}
data_valid_keys = ['message', 'action']

ACTIONS = {'SET_VIDS': 'set_vids',
           'SET_CHARACTER_STATUS': 'set_character_status',
           'SET_HACK_STATUS': 'set_hack_status',
           'SET_INVENTORY_STATUS': 'set_inventory_status',
           'SET_PICKUP_FILTER': 'set_pickup_filter',
           'APPEND_SHOP_SEARCH': 'append_shop_search',
           }

class MetinMemoryObject:

    def __init__(self):
        self.encoding = ''
        self.character_status = {
            'vid': 0,
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
            'FishBot': {},
            'ChannelSwitcher': {},
            'FileHandler': {},
            'InstanceInteractions': {},
            'Protector': {}}
        self.InstancesList = []
        self.Equipment = {}  # Items worn
        self.Inventory = []  # Items in inventory
        self.free_inventory_slots = 0
        self.max_inventory_slots = 0
        self.PickupFilter = []  # List with item's id to pickup
        self.ScannedShops = []

    def OnReceiveInformation(self, received_information):
        if not self.ValidateReceivedInformation(received_information):
            print('cleaned_information is empty')
            return False

        if received_information['action'] == ACTIONS['SET_VIDS']:
            self.InstancesList = [instance for instance in received_information['data']]
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
            self.free_inventory_slots = received_information['data']['FreeSlots']
            self.max_inventory_slots = received_information['data']['MaxInventorySize']
            return True

        if received_information['action'] == ACTIONS['SET_PICKUP_FILTER']:
            self.PickupFilter = received_information['data']
            return True

        if received_information['action'] == ACTIONS['APPEND_SHOP_SEARCH']:
            self.ScannedShops.append(received_information['data']['Shop'])
            return True



    def ValidateReceivedInformation(self, received_information):
        if received_information['action'] == ACTIONS['SET_VIDS']:
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

        elif received_information['action'] == ACTIONS['SET_CHARACTER_STATUS']:
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

        elif received_information['action'] == ACTIONS['SET_HACK_STATUS']:
            if not type(received_information['data']) == dict:
                print('data is not dict')
                return False

            for message_key in received_information['data'].keys():
                if message_key not in self.hack_options.keys():
                    print(message_key, ' is not in hack options')
                    return False

        return True

    def ReturnServerItemList(self, PATH: str, language: str):
        return FileLoader.load_item_list(PATH, language)

    def ReturnServerMobList(self, PATH: str, language: str):
        return FileLoader.load_mob_list(PATH, language)

    def ReturnServerSkillList(self, PATH: str, language: str):
        return FileLoader.load_skill_names(PATH, language)

    def ReturnItemIconsNames(self, PATH: str):
        return FileLoader.load_item_icon(PATH)