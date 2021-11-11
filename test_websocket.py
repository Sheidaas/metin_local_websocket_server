import _websocket
import simplejson as json

web_socket = _websocket.WebsocketServer('127.0.0.1', 1234)
web_socket.metin_clients = [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}]
web_socket.frontend_clients = [{'id': 5}, {'id': 6}, {'id': 7}, {'id': 8}, {'id': 9}]


def test_client_by_id():
    assert web_socket.get_client_by_id(3) == {'id': 3}

    assert web_socket.get_client_by_id(8) == {'id': 8}

    assert web_socket.get_client_by_id(20) is None


def test_remove_client_by_id():
    assert web_socket.remove_client_by_id(3)
    assert web_socket.remove_client_by_id(3) is False
    assert web_socket.remove_client_by_id(7)
    assert web_socket.remove_client_by_id(7) is False


def test_get_metin_memory_object_by_client_id():
    client_id = 5
    assert web_socket.get_memory_object_by_client_id(client_id) is None

    web_socket.create_new_metin_memory_object(client_id, 'testing-encoding')
    assert web_socket.get_memory_object_by_client_id(client_id)


def test_create_new_metin_memory_object():
    client_id = 7
    assert web_socket.create_new_metin_memory_object(client_id, 'testing-encoding')
    assert web_socket.create_new_metin_memory_object(client_id, 'testing-encoding') is False


def test_remove_memory_object_by_client_id():
    assert web_socket.remove_memory_object_by_client_id(7)
    assert web_socket.remove_memory_object_by_client_id(7) is False


def test_is_client_new():
    client = {'id': 1}
    assert web_socket.is_client_new(client) == web_socket.metin_clients
    client = {'id': 9}
    assert web_socket.is_client_new(client) == web_socket.frontend_clients
    client = {'id': -4}
    assert web_socket.is_client_new(client) is False


def test_validate_message():
    invalid_json_message = 'safashlfasdh'
    # checking that is validate_message accept non-json message
    assert web_socket.validate_message(invalid_json_message) is False

    # checking message with wrong keys
    invalid_json_message = json.dumps({'something': ''})
    assert web_socket.validate_message(invalid_json_message) is False


