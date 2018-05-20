import server
import time

def test_chk_ip_value():
    assert not server._chk_ip_value('127.0.0.l')
    assert not server._chk_ip_value('127001')
    assert not server._chk_ip_value('string_by_mistake')
    assert not server._chk_ip_value('335.0.0.l')
    assert server._chk_ip_value('127.0.0.1')
    assert not server._chk_ip_value('0.127.0.l')
# server = server.Server('127.0.0.1, 7777')

def test_chk_port_value():
    assert server._chk_port_value(7777)
    assert not server._chk_port_value('asd')
    assert not server._chk_port_value(80)
    assert not server._chk_port_value(808080)

class TestServer:


    def test_chk_fields(self):
        x = server.Server('127.0.0.1', 7777)
        messages = [{'time': time.time(), 'login': 'max'},
                    {'action': 'presence', 't1me': time.time(), 'login': 'max'},
                    {'action': 'presence_might_to_be_alive_forever', 'time': time.time(), 'login': 'max'}
        ]
        for message in messages:
            assert not x.chk_fields(message)

        assert x.chk_fields({'action': 'presence', 'time': time.time(), 'login': 'max'})

    def test_create_response(self):
        x = server.Server('127.0.0.1', 7777)
        values = [('200', {'new_key':'new_value'}), ('400', {'another_key':123})]
        good_responses = [{'response': '200', 'time': 'time'},
                          {'response': '200', 'time': 'time', 'new_key':'new_value'},
                          {'response': '400', 'time': 'time', 'another_key':123}
                          ]
        for value in values:
            response = x.create_response(value[0], **value[1])
            assert response in  good_responses

test = TestServer()
test.test_create_response()