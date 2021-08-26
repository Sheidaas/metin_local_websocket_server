instance_valid_keys = {'id': int, 'x': int, 'y': int, 'type': int, 'vid': int}
data_valid_keys = ['message', 'action']


class MetinMemoryObject:

    def __init__(self):
        self.character_status = {
            'Position': [float, float],
            'CurrentMap': 'None',
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
        }
        self.InstancesList = []

    def OnReceiveInformation(self, received_information):
        #print(received_information)
        if not self.ValidateReceivedInformation(received_information):
            print('cleaned_information is empty')
            return False

        if received_information['action'] == 'set_vids':
            self.InstancesList = [None] * len(received_information['data'])
            for instance in range(len(received_information['data'])):
                self.InstancesList[instance] = received_information['data'][instance]
        #print(self.InstancesList)
        #print('that was instances list')
            return True

        if received_information['action'] == 'set_character_status':
            for status_key in received_information['data'].keys():
                self.character_status[status_key] = received_information['data'][status_key]
            #print(self.character_status)
            
            return True

    def ValidateReceivedInformation(self, received_information):

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

        if received_information['action'] == 'set_character_status':
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

        return True

