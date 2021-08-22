import websocket
import _thread
import json
PACKETS_PATTERNS = {
    'hearthbeat': {'type': 'hearthbeat', 'data': {'message': 'hearthbeat'}},
    'set_role_as_metin_client': {'type': 'set_role', 'data': {'message': 'metin2_client'}},
    'set_role_as_front_client': {'type': 'set_role', 'data': {'message': 'front_client'}},
    'bad': "fdsafdasfdafsda",
}
def on_open(ws):
    ws.send('frontend_client')

ws = websocket.create_connection('ws://127.0.0.1:13254')
print(json.loads(ws.recv()))
ws.send(json.dumps(PACKETS_PATTERNS['hearthbeat']))
print(json.loads(ws.recv()))
ws.send(json.dumps(PACKETS_PATTERNS['set_role_as_front_client']))
print(json.loads(ws.recv()))
ws.send(PACKETS_PATTERNS['bad'])
print(json.loads(ws.recv()))