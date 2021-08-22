import websocket_server
import logging
import json
from Modules.MetinMemoryObject import MetinMemoryObject


PACKETS_PATTERNS_TYPES = {
    'unknow': 'unknow',
    'hearthbeat': 'hearthbeat',
    'result': 'result',
    'informations': 'informations'
    }

PACKETS_PATTERNS = {
    'unknow_request': {'type': PACKETS_PATTERNS_TYPES['unknow'], 'data': {'message': 'unknow'}},
    'hearthbeat': {'type': PACKETS_PATTERNS_TYPES['hearthbeat'], 'data': {'message': 'hearthbeat'}},
    'result_confirmed': {'type': PACKETS_PATTERNS_TYPES['result'], 'data': {'message': 'confirmed'}},
    'result_denied': {'type': PACKETS_PATTERNS_TYPES['result'], 'data': {'message': 'denied'}},
}

RECEIVED_PACKETS_PATTERNS_TYPES = {
    'hearthbeat': 'hearthbeat',
    'set_role': 'set_role',
    'information': 'information'
}

PACKET_GOOD_KEYS = ['type', 'data']
DATA_GOOD_KEYS = ['message', 'action', 'memory']
ACTION_GOOD_KEYS = ['append', 'remove']
MEMORY_GOOD_KEYS = ['metin_memory_object']

class WebsocketServer:

    def __init__(self, host, port):
        self.all_clients = []

        self.metin_clients = []
        self.metin_memory_objects = []

        self.frontend_clients = []

        self.server = websocket_server.WebsocketServer(port, host=host, loglevel=logging.INFO)

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
        server.send_message(client, json.dumps(PACKETS_PATTERNS['result_confirmed']))

    def client_left(self, client, server):
        client_list = self.is_client_new(client)
        if not client_list:
            return
        client_list.remove(client)
        return
    
    def ValidateMessage(self, message):
        try:
            json_message = json.loads(message)
        except:
            print('This is not a json message')
            return False
        
        message_keys = json_message.keys()
        #print(message_keys)
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
                    print(str(json_message[message_key]) + 'is not there ' + RECEIVED_PACKETS_PATTERNS_TYPES.keys())
                    return False

            if message_key == 'data':
                if not type(json_message[message_key]) == dict: 
                    print(str(json_message[message_key]) + 'is not a dict ')
                    return False
                    
                for data_key in json_message[message_key].keys():
                    if data_key not in DATA_GOOD_KEYS:
                        print(data_key + ' is not in ' + DATA_GOOD_KEYS)
                        return False

            if message_key == 'action':
                if json_message[message_key] not in ACTION_GOOD_KEYS:
                    print(str(json_message[message_key]) + 'is not there ' + ACTION_GOOD_KEYS)
                    return False 
            
            if message_key == 'memory':
                if json_message[message_key] not in MEMORY_GOOD_KEYS:
                    print(str(json_message[message_key]) + 'is not there ' + MEMORY_GOOD_KEYS)
                    return False            

        return json_message

    def message_received(self, client, server, message):
        
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
                    #print('this is metin2 client')
                    self.client_list.remove(client)
                    self.metin_clients.append(client)
                    server.send_message(client, json.dumps(PACKETS_PATTERNS['result_confirmed']))
                    return
                
                elif cleared_message['data']['message'] == 'front_client':
                    #print('this is front client')
                    client_list.remove(client)
                    self.metin_clients.append(client)
                    server.send_message(client, json.dumps(PACKETS_PATTERNS['result_confirmed']))
                    return
                
                else:
                    #print('This is else')
                    server.send_message(client, json.dumps(PACKETS_PATTERNS['unknow_request']))
                    return

        if client_list == self.metin_clients:

            if cleared_message['type'] == RECEIVED_PACKETS_PATTERNS_TYPES['information']:

                received_information = {
                    'action': cleared_message['data']['action'],
                    'data': cleared_message['data']['message']
                }
                memory_object = self.get_memory_object_by_client_id(client['id'])
                if memory_object == None:
                    memory_object = {
                        'client_id': client['id'],
                        'object': MetinMemoryObject(),
                    }
                    self.metin_memory_objects.append(memory_object)
                result = memory_object['object'].OnReceiveInformations(received_information) # This will validate data and stuff
                if result: 
                    server.send_message(client, json.dumps(PACKETS_PATTERNS['result_confirmed']))
                    return
                server.send_message(client, json.dumps(PACKETS_PATTERNS['unknow_request']))
                return

    def run_server(self):
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_message_received(self.message_received)
        self.server.set_fn_client_left(self.client_left)
        self.server.run_forever()

server = WebsocketServer('127.0.0.1', 13254)
server.run_server()