import logging
import os
import pkg_resources
import sys
import subprocess
from Modules.MetinMemoryObject import MetinMemoryObject
import Modules.FileLoader as FileLoader

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)))


PACKETS_PATTERNS_TYPES = {
    'unknow': 'unknow',
    'hearthbeat': 'hearthbeat',
    'result': 'result',
    'information': 'information',
    'update_state': 'update_state',
    'update_frontend_client': 'update_frontend_client'
}

PACKETS_PATTERNS = {
    'unknow_request': {'type': PACKETS_PATTERNS_TYPES['unknow'], 'data': {'message': 'unknow'}},
    'hearthbeat': {'type': PACKETS_PATTERNS_TYPES['hearthbeat'], 'data': {'message': 'hearthbeat'}},
    'result_confirmed': {'type': PACKETS_PATTERNS_TYPES['result'], 'data': {'message': 'confirmed'}},
    'result_denied': {'type': PACKETS_PATTERNS_TYPES['result'], 'data': {'message': 'denied'}},
    'all_clients': {'type': PACKETS_PATTERNS_TYPES['update_state'], 'data': {'message': []}},
    'set_inventory_status': {'type': PACKETS_PATTERNS_TYPES['information'], 'data': {'message': [], 'action': 'set_inventory_status'}}
}

RECEIVED_PACKETS_PATTERNS_TYPES = {
    'actions': 'actions',
    'hearthbeat': 'hearthbeat',
    'set_role': 'set_role',
    'information': 'information',
    'update': 'update',
    'update_request': 'update_request',
    'update_frontend_client': 'update_frontend_client'
}

PACKET_GOOD_KEYS = ['type', 'data']
DATA_GOOD_KEYS = ['message', 'action', 'memory', 'client_id', 'module', 'schema',
                  'options', 'needed_options', 'language']


ACTION_GOOD_KEYS = ['append', 'remove']
MEMORY_GOOD_KEYS = ['metin_memory_object']

ACTIONS = {
    'GET_ALL_CONNECTED_METIN_CLIENTS': 'GET_ALL_CONNECTED_METIN_CLIENTS',
    'GET_FULL_CHARACTER_STATUS': 'GET_FULL_CHARACTER_STATUS',
    'GET_FULL_INSTANCES_LIST': 'GET_FULL_INSTANCES_LIST',
    'GET_FULL_HACK_STATUS': 'GET_FULL_HACK_STATUS',
    'GET_FULL_SERVER_STATUS': 'GET_FULL_SERVER_STATUS',
    'GET_INVENTORY_STATUS': 'GET_INVENTORY_STATUS',
    'SET_INVENTORY_STATUS': 'SET_INVENTORY_STATUS',
    'GET_PICKUP_FILTER': 'GET_PICKUP_FILTER',
    'SET_PICKUP_FILTER': 'SET_PICKUP_FILTER',
    'SET_NEW_SCHEMA': 'SET_NEW_SCHEMA',
    'CHANGE_FRONTEND_LANGUAGE': 'CHANGE_FRONTEND_LANGUAGE',
    'GET_SCANNED_SHOPS': 'GET_SCANNED_SHOPS',
}


class WebsocketServer:

    def __init__(self):
        self.all_clients = []

        self.metin_clients = []
        self.metin_memory_objects = []

        self.frontend_clients = []

        self.server = websocket_server.WebsocketServer( '127.0.0.1', 13254, loglevel=logging.INFO)

    def get_client_by_id(self, client_id: int):
        for client in self.metin_clients:
            if client['id'] == client_id:
                return client

        for client in self.frontend_clients:
            if client['id'] == client_id:
                return client

        return None

    def remove_client_by_id(self, client_id: int):
        for client in self.metin_clients:
            if client['id'] == client_id:
                self.metin_clients.remove(client)
                return True

        for client in self.frontend_clients:
            if client['id'] == client_id:
                self.frontend_clients.remove(client)
                return True

        return False

    def create_new_metin_memory_object(self, metin_client_id: int, encoding: str):
        memory_object = self.get_memory_object_by_client_id(metin_client_id)
        if memory_object is None:
            memory_object = {
                'client_id': metin_client_id,
                'object': MetinMemoryObject(),
            }
            memory_object['object'].encoding = encoding
            self.metin_memory_objects.append(memory_object)
            return True
        return False

    def remove_memory_object_by_client_id(self, client_id: int):
        for memory_object in self.metin_memory_objects:
            if memory_object['client_id'] == client_id:
                self.metin_memory_objects.remove(memory_object)
                return True
        return False 

    def get_memory_object_by_client_id(self, client_id: int):
        for memory_object in self.metin_memory_objects:
            if memory_object['client_id'] == client_id:
                return memory_object
        return None

    def is_client_new(self, client):
        if client['id'] in [_client['id'] for _client in self.all_clients]:
            return self.all_clients
        elif client['id'] in [_client['id'] for _client in self.metin_clients]:
            return self.metin_clients
        elif client['id'] in [_client['id'] for _client in self.frontend_clients]:
            return self.frontend_clients
        return False

    def new_client(self, client, server):
        self.all_clients.append(client)
        server.send_message(client, json.dumps(PACKETS_PATTERNS['result_confirmed']))

    def client_left(self, client, server):
        client_list = self.is_client_new(client)
        if not client_list:
            return
        self.remove_client_by_id(client['id'])
        self.remove_memory_object_by_client_id(client['id'])
        return

    @staticmethod
    def validate_message(message):
        try:
            json_message = json.loads(message)
        except Exception as e:
            print(e)
            print('This is not a json message')
            return False
        
        if type(json_message) == list:
            json_message = json_message[0]
        
        message_keys = json_message.keys()
        for message_key in message_keys:
            if message_key not in PACKET_GOOD_KEYS:
                print('Message keys are not in packet_good_keys')
                return False
        
        for required_key in PACKET_GOOD_KEYS:
            if required_key not in message_keys:
                return False

        for message_key in message_keys:

            if message_key == 'type':
                if json_message[message_key] not in RECEIVED_PACKETS_PATTERNS_TYPES.keys():
                    print(str(json_message[message_key]) + 'is not there '
                          + str(RECEIVED_PACKETS_PATTERNS_TYPES.keys()))
                    return False

            if message_key == 'data':
                if not type(json_message[message_key]) == dict: 
                    print(str(json_message[message_key]) + ' is not a dict ')
                    return False
                    
                for data_key in json_message[message_key].keys():
                    if data_key not in DATA_GOOD_KEYS:
                        print(data_key, ' is not in ', DATA_GOOD_KEYS)
                        return False

            if message_key == 'action':
                if json_message[message_key] not in ACTION_GOOD_KEYS:
                    print(str(json_message[message_key]) + ' is not there ' + str(ACTION_GOOD_KEYS))
                    return False 
            
            if message_key == 'memory':
                if json_message[message_key] not in MEMORY_GOOD_KEYS:
                    print(str(json_message[message_key]) + ' is not there ' + str(MEMORY_GOOD_KEYS))
                    return False            

        #print(json_message['data'].keys())
        if 'message' not in json_message['data'].keys():
            return False

        if json_message['type'] == 'actions':
            if not type(json_message['data']['message']) == list:
                return False
            
            if not (len(json_message['data']['message'])):
                return False
            try:
                if not type(json_message['data']['message'][0]['function_args']) == list:
                    return False      
            except KeyError:
                return False     

        return json_message

    def message_received(self, client, server, message):
        cleared_message = self.validate_message(message)
        if not cleared_message:
            server.send_message(client, json.dumps(PACKETS_PATTERNS['unknow_request']))
            return

        client_list = self.is_client_new(client)
        if not client_list:
            server.send_message(client, json.dumps(PACKETS_PATTERNS['result_denied']))
            return

        if cleared_message['type'] == RECEIVED_PACKETS_PATTERNS_TYPES['hearthbeat']:
            server.send_message(client, json.dumps(PACKETS_PATTERNS['hearthbeat']))
            return

        if client_list == self.all_clients:

            if cleared_message['type'] == RECEIVED_PACKETS_PATTERNS_TYPES['set_role']:
                if cleared_message['data']['message'] == 'metin2_client':
                    print('New metin2 client joined')
                    client_list.remove(client)
                    self.metin_clients.append(client)
                    self.create_new_metin_memory_object(client['id'], cleared_message['data']['language'])
                    server.send_message(client, json.dumps(PACKETS_PATTERNS['result_confirmed']))
                    return
                
                elif cleared_message['data']['message'] == 'frontend_client':
                    print('New frontend client joined')
                    client_list.remove(client)
                    front_client = {
                        'id': client['id'],
                        'handler': client['handler'],
                        'address': client['address'],
                        'options': {
                            'language': 'en',
                            'save_mob_locations_to_db': False,
                        }}
                    self.frontend_clients.append(front_client)
                    server.send_message(client, json.dumps(PACKETS_PATTERNS['result_confirmed']))
                    return

        elif client_list == self.metin_clients:
            if cleared_message['type'] == RECEIVED_PACKETS_PATTERNS_TYPES['information']:
                received_information = {
                    'action': cleared_message['data']['action'],
                    'data': cleared_message['data']['message']
                }
                memory_object = self.get_memory_object_by_client_id(client['id'])
                if memory_object is None:
                    memory_object = {
                        'client_id': client['id'],
                        'object': MetinMemoryObject(),
                    }
                    self.metin_memory_objects.append(memory_object)
                result = memory_object['object'].OnReceiveInformation(received_information) # This will validate data and stuff
                if result: 
                    server.send_message(client, json.dumps(PACKETS_PATTERNS['result_confirmed']))
                    return
                server.send_message(client, json.dumps(PACKETS_PATTERNS['unknow_request']))
                return

        elif client_list == self.frontend_clients:

            if cleared_message['type'] == RECEIVED_PACKETS_PATTERNS_TYPES['information']:

                if cleared_message['data']['action'] == ACTIONS['GET_ALL_CONNECTED_METIN_CLIENTS']:
                    clients = []
                    for metin_client in self.metin_clients:
                        memory_object = self.get_memory_object_by_client_id(metin_client['id'])
                        if memory_object is not None:
                            clients.append ({
                                'id': metin_client['id'],
                                'address': metin_client['address'],
                                'player_position': memory_object['object'].character_status['Position'],
                                'player_name': memory_object['object'].character_status['Name'],
                                'player_level': memory_object['object'].character_status['Level'],
                                'player_experience': memory_object['object'].character_status['Experience'],
                                'player_max_experience': memory_object['object'].character_status['MaxExperience'],
                                'player_curr_map': memory_object['object'].character_status['CurrentMap'],
                                })

                    message = {'type': PACKETS_PATTERNS_TYPES['information'], 'data': {'message': clients, 'action': ACTIONS['GET_ALL_CONNECTED_METIN_CLIENTS']}}

                    server.send_message(client, json.dumps(message))

                if cleared_message['data']['action'] == ACTIONS['GET_FULL_CHARACTER_STATUS']:
                    
                    memory_object = self.get_memory_object_by_client_id(cleared_message['data']['message'])
                    if memory_object is not None:
                        character_status = memory_object['object'].character_status
                        message = {'type': PACKETS_PATTERNS_TYPES['information'], 'data': {'message': character_status, 'action': ACTIONS['GET_FULL_CHARACTER_STATUS']}}
                        server.send_message(client, json.dumps(message))
                
                if cleared_message['data']['action'] == ACTIONS['GET_FULL_INSTANCES_LIST']:
                    from Modules.StatisticsDatabase import statDB
                    client = self.get_client_by_id(client['id'])
                    memory_object = self.get_memory_object_by_client_id(cleared_message['data']['message'])
                    if memory_object is not None:
                        instances_list = memory_object['object'].InstancesList
                        if client['options']['save_mob_locations_to_db']:
                            statDB.AddNewMobData(instances_list, memory_object['object'].character_status['CurrentMap'])

                        message = {'type': PACKETS_PATTERNS_TYPES['information'], 'data': {'message': instances_list, 'action': ACTIONS['GET_FULL_INSTANCES_LIST']}}
                        server.send_message(client, json.dumps(message))

                if cleared_message['data']['action'] == ACTIONS['GET_FULL_HACK_STATUS']:
                    memory_object = self.get_memory_object_by_client_id(cleared_message['data']['message'])
                    if memory_object is not None:
                        hack_status = memory_object['object'].hack_options
                        message = {'type': PACKETS_PATTERNS_TYPES['information'],
                                   'data': {'message': hack_status, 'action': ACTIONS['GET_FULL_HACK_STATUS']}}
                        server.send_message(client, json.dumps(message))

                if cleared_message['data']['action'] == ACTIONS['GET_FULL_SERVER_STATUS']:
                    memory_object = self.get_memory_object_by_client_id(cleared_message['data']['message'])
                    client = self.get_client_by_id(client['id'])
                    client['options']['language'] = cleared_message['data']['language'].lower()
                    if memory_object is not None:
                        server_info = {
                            'Items': memory_object['object'].ReturnServerItemList(PATH, client['options']['language']),
                            'Mobs': memory_object['object'].ReturnServerMobList(PATH, client['options']['language']),
                            'Skills': memory_object['object'].ReturnServerSkillList(PATH, client['options']['language']),
                            'ItemIcons': memory_object['object'].ReturnItemIconsNames(PATH)
                        }
                        message = {'type': PACKETS_PATTERNS_TYPES['information'], 'data': {'message': server_info, 'action': ACTIONS['GET_FULL_SERVER_STATUS']}}
                        server.send_message(client, json.dumps(message))

                if cleared_message['data']['action'] == ACTIONS['GET_SCANNED_SHOPS']:
                    memory_object = self.get_memory_object_by_client_id(cleared_message['data']['client_id'])
                    if memory_object is not None:
                        scanned_shops = {
                            'ScannedShops': memory_object['object'].ScannedShops
                        }
                        message = {'type': PACKETS_PATTERNS_TYPES['information'], 'data': {'message': scanned_shops, 'action': ACTIONS['GET_SCANNED_SHOPS']}}
                        server.send_message(client, json.dumps(message))
                        memory_object['object'].ScannedShops = []


            elif cleared_message['type'] == RECEIVED_PACKETS_PATTERNS_TYPES['actions']:
                client_to_send = self.get_client_by_id(cleared_message['data']['client_id'])
                if client_to_send is None:
                    return
                server.send_message(client_to_send, json.dumps(cleared_message, ensure_ascii=False))

            elif cleared_message['type'] == RECEIVED_PACKETS_PATTERNS_TYPES['update']:
                client_to_send = self.get_client_by_id(cleared_message['data']['client_id'])
                if client_to_send is None:
                    return

                server.send_message(client_to_send, json.dumps(cleared_message))

            elif cleared_message['type'] == RECEIVED_PACKETS_PATTERNS_TYPES['update_request']:
                client_to_send = self.get_client_by_id(int(cleared_message['data']['message']))
                if client_to_send is None:
                    return

                if cleared_message['data']['action'] == ACTIONS['GET_INVENTORY_STATUS']:
 
                    server.send_message(client_to_send, json.dumps(cleared_message))

                    memory_object = self.get_memory_object_by_client_id(cleared_message['data']['message'])
                    if memory_object is not None:
                        inventory = {
                            'Inventory': memory_object['object'].Inventory,
                            'Equipment': memory_object['object'].Equipment,
                            'FreeSlots': memory_object['object'].free_inventory_slots,
                            'MaxInventorySize': memory_object['object'].max_inventory_slots,
                        }

                        message = {'type': PACKETS_PATTERNS_TYPES['information'],
                                   'data': {'message': inventory, 'action': ACTIONS['SET_INVENTORY_STATUS']}}
                        server.send_message(client, json.dumps(message))  

                elif cleared_message['data']['action'] == ACTIONS['GET_PICKUP_FILTER']:
                    server.send_message(client_to_send, json.dumps(cleared_message))
                    memory_object = self.get_memory_object_by_client_id(cleared_message['data']['message'])
                    if memory_object is not None:
                        PickupFilter = {
                            'PickupFilter': memory_object['object'].PickupFilter
                        }
                        message = {'type': PACKETS_PATTERNS_TYPES['information'], 'data': {'message': PickupFilter, 'action': ACTIONS['SET_PICKUP_FILTER']}}
                        server.send_message(client, json.dumps(message))        

                elif cleared_message['data']['action'] == ACTIONS['SET_NEW_SCHEMA']:
                    schema = FileLoader.load_schema_by_name(PATH, cleared_message['data']['schema'])
                    schema['OPTIONS'] = cleared_message['data']['options']
                    schema['NEEDED_OPTIONS'] = cleared_message['data']['needed_options']
                    message = {'type': RECEIVED_PACKETS_PATTERNS_TYPES['update_request'], 'data':{'message': schema, 'action': ACTIONS['SET_NEW_SCHEMA']}}
                    server.send_message(client_to_send, json.dumps(message))






    def run_server(self):
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_message_received(self.message_received)
        self.server.set_fn_client_left(self.client_left)
        self.server.run_forever()


def check_installed_packages():
    required = {'websocket_server', 'simplejson', 'tinydb'}
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        python = sys.executable
        print("Upgrading pip")
        subprocess.check_call([python, '-m', 'pip', 'install', '--upgrade', ' pip'], stdout=subprocess.DEVNULL)
        print("Going to install")
        print(missing)
        subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)

    global websocket_server, json
    import websocket_server, simplejson as json


def main():
    check_installed_packages()

    server = WebsocketServer()
    server.run_server()


if __name__ == '__main__':
    main()
