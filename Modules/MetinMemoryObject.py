instance_valid_keys = {'id': int, 'x': int, 'y': int, 'type': int, 'vid': int}
data_valid_keys = ['message', 'action']


class MetinMemoryObject:

    def __init__(self):
        self.InstancesList = []

    def OnReceiveInformation(self, received_information):
        if not self.ValidateReceivedInformation(received_information):
            print('cleaned_information is empty')
            return False

        if received_information['action'] == 'set_vids':
            self.InstancesList = [None] * len(received_information['data'])
            for instance in range(len(received_information['data'])):
                self.InstancesList[instance] = received_information['data'][instance]
        print(self.InstancesList)
        print('that was instances list')
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

        return True

