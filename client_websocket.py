import websocket
import _thread
import json

append_vids = [
    {'id': 0, 'x': 0, 'y': 0, 'type': 0, 'vid': 0},
    {'id': 0, 'x': 15, 'y': 18, 'type': 0, 'vid': 5},
    {'id': 1, 'x': 87, 'y': 65, 'type': 1, 'vid': 1},
    {'id': 0, 'x': 12, 'y': 92, 'type': 0, 'vid': 6},
]

PACKETS_PATTERNS = {
    'hearthbeat': {'type': 'hearthbeat', 'data': {'message': 'hearthbeat'}},
    'set_role_as_metin_client': {'type': 'set_role', 'data': {'message': 'metin2_client'}},
    'set_role_as_front_client': {'type': 'set_role', 'data': {'message': 'front_client'}},
    'send_information_vid_mobs': {'type': 'information', 'data': {'message': append_vids, 'action': 'append_vids'}},
    'bad': "fdsafdasfdafsda",
}


def on_open(ws):
    ws.send('frontend_client')


ws = websocket.create_connection('ws://127.0.0.1:13254')
print(json.loads(ws.recv()))
ws.send(json.dumps(PACKETS_PATTERNS['hearthbeat']))
print(json.loads(ws.recv()))
ws.send(json.dumps(PACKETS_PATTERNS['set_role_as_metin_client']))
print(json.loads(ws.recv()))
ws.send(json.dumps(PACKETS_PATTERNS['send_information_vid_mobs']))
print(json.loads(ws.recv()))
