import client
import time

class TestClient:

    def test_create_presense(self):
        x = client.Client('127.0.0.1', 7777)
        arg = {'trying to add':'new key and value'}
        presence = x.create_presence(**arg)
        print(presence)
        current_time = time.time()
        assert 'action' and 'time' and 'login' in presence\
        and presence['action'] == 'presence' and presence['login'] == 'max'\
        and (presence['time'] - current_time)<0.01\
        and presence['trying to add'] == 'new key and value'
        del x

    def test_dict_to_bytes_and_bytes_to_dict(self):
        x = client.Client('127.0.0.1', 7777)
        messages = [
            {'response': '200', 'time': 'time'},
            {'response': '200', 'time': 'time', 'new_key':'new_value'},
            {'response': '400', 'time': 'time', 'another_key': 123}
        ]
        for message in messages:
            b = client._dict_to_bytes(message)
            d = client._bytes_to_dict(b)
            assert d == message
        del x