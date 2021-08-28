import websocket_server
import logging
import simplejson as json
from Modules.MetinMemoryObject import MetinMemoryObject


PACKETS_PATTERNS_TYPES = {
    'unknow': 'unknow',
    'hearthbeat': 'hearthbeat',
    'result': 'result',
    'information': 'information',
    'update_state': 'update_state'
    }

PACKETS_PATTERNS = {
    'unknow_request': {'type': PACKETS_PATTERNS_TYPES['unknow'], 'data': {'message': 'unknow'}},
    'hearthbeat': {'type': PACKETS_PATTERNS_TYPES['hearthbeat'], 'data': {'message': 'hearthbeat'}},
    'result_confirmed': {'type': PACKETS_PATTERNS_TYPES['result'], 'data': {'message': 'confirmed'}},
    'result_denied': {'type': PACKETS_PATTERNS_TYPES['result'], 'data': {'message': 'denied'}},
    'all_clients': {'type': PACKETS_PATTERNS_TYPES['update_state'], 'data': {'message': []}}
}

RECEIVED_PACKETS_PATTERNS_TYPES = {
    'actions': 'actions',
    'hearthbeat': 'hearthbeat',
    'set_role': 'set_role',
    'information': 'information'
}

PACKET_GOOD_KEYS = ['type', 'data']
DATA_GOOD_KEYS = ['message', 'action', 'memory', 'client_id']
ACTION_GOOD_KEYS = ['append', 'remove']
MEMORY_GOOD_KEYS = ['metin_memory_object']

class WebsocketServer:

    def __init__(self, host, port):
        self.all_clients = []

        self.metin_clients = []
        self.metin_memory_objects = []

        self.frontend_clients = []

        self.server = websocket_server.WebsocketServer(port, host=host, loglevel=logging.INFO)

    def get_client_by_id_and_list(self, client_list, client_id):
        for client in client_list:
            if client['id'] == client_id:
                return client
        return None

    def get_memory_object_by_client_id(self, client_id):
        for memory_object in self.metin_memory_objects:
            if memory_object['client_id'] == client_id:
                return memory_object
        return None

    def is_client_new(self, client):
        if client in self.all_clients:
            return self.all_clients
        elif client in self.metin_clients:
            return self.metin_clients
        elif client in self.frontend_clients:
            return self.frontend_clients
        else:
            return False

    def new_client(self, client, server):
        self.all_clients.append(client)
        print('New client joined')
        server.send_message(client, json.dumps(PACKETS_PATTERNS['result_confirmed']))

    def client_left(self, client, server):
        client_list = self.is_client_new(client)
        if not client_list:
            return
        client_list.remove(client)
        return
    
    def ValidateMessage(self, message):
        #print(message)
        try:
            json_message = json.loads(message)
        except:
            print('This is not a json message, validate message')
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
                    print(str(json_message[message_key]) + 'is not there ' + str(RECEIVED_PACKETS_PATTERNS_TYPES.keys()))
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
                    print(str(json_message[message_key]) + ' is not there ' + ACTION_GOOD_KEYS)
                    return False 
            
            if message_key == 'memory':
                if json_message[message_key] not in MEMORY_GOOD_KEYS:
                    print(str(json_message[message_key]) + ' is not there ' + MEMORY_GOOD_KEYS)
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
        #print(message)
        cleared_message = self.ValidateMessage(message)
        #print(cleared_message)
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
                #print('This is a set_role message')
                #print(type(cleared_message['data']['message']))


                if cleared_message['data']['message'] == 'metin2_client':
                    print('this is metin2 client')
                    client_list.remove(client)
                    self.metin_clients.append(client)
                    server.send_message(client, json.dumps(PACKETS_PATTERNS['result_confirmed']))
                    return
                
                elif cleared_message['data']['message'] == 'frontend_client':
                    print('this is frontend_client')
                    client_list.remove(client)
                    self.frontend_clients.append(client)
                    server.send_message(client, json.dumps(PACKETS_PATTERNS['result_confirmed']))
                    return
                
                else:
                    #print('This is else')
                    server.send_message(client, json.dumps(PACKETS_PATTERNS['unknow_request']))
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
            #print(str(cleared_message))
            if cleared_message['type'] == RECEIVED_PACKETS_PATTERNS_TYPES['information']:

                if cleared_message['data']['action'] == 'get_all_connected_metin_clients':
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

                    #print(clients)
                    message = {'type': PACKETS_PATTERNS_TYPES['information'], 'data': {'message': clients, 'action': 'get_all_connected_metin_clients'}}
                    
                    server.send_message(client, json.dumps(message))

                if cleared_message['data']['action'] == 'get_full_character_status':
                    
                    memory_object = self.get_memory_object_by_client_id(cleared_message['data']['message'])
                    if memory_object is not None:
                        character_status = memory_object['object'].character_status
                        message = {'type': PACKETS_PATTERNS_TYPES['information'], 'data': {'message': character_status, 'action': 'get_full_character_status'}}
                        server.send_message(client, json.dumps(message))
                
                if cleared_message['data']['action'] == 'get_full_instances_list':
                    memory_object = self.get_memory_object_by_client_id(cleared_message['data']['message'])
                    if memory_object is not None:
                        instances_list = memory_object['object'].InstancesList
                        message = {'type': PACKETS_PATTERNS_TYPES['information'], 'data': {'message': instances_list, 'action': 'get_full_instances_list'}}
                        server.send_message(client, json.dumps(message))

                if cleared_message['data']['action'] == 'get_full_hack_status':
                    memory_object = self.get_memory_object_by_client_id(cleared_message['data']['message'])
                    if memory_object is not None:
                        hack_status = memory_object['object'].hack_options
                        message = {'type': PACKETS_PATTERNS_TYPES['information'], 'data': {'message': hack_status, 'action': 'get_full_hack_status'}}
                        server.send_message(client, json.dumps(message))

            elif cleared_message['type'] == RECEIVED_PACKETS_PATTERNS_TYPES['actions']:
                client_to_send = self.get_client_by_id_and_list(self.metin_clients, cleared_message['data']['client_id'])
                if client_to_send is None:
                    return
                
                for action in cleared_message['data']['message']:
                    for action_key in action.keys():
                        if type(action[action_key]) == str:
                            action[action_key] = action[action_key].encode('utf-8')

                server.send_message(client_to_send, json.dumps(cleared_message, ensure_ascii=False))

    def run_server(self):
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_message_received(self.message_received)
        self.server.set_fn_client_left(self.client_left)
        self.server.run_forever()

server = WebsocketServer('127.0.0.1', 13254)
server.run_server()