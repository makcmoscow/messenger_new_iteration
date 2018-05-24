import server
import time
import socket


def test_chk_ip_value():
    assert server._chk_ip_value('127.0.0.1')
    assert not server._chk_ip_value('127.0.0.l')
    assert not server._chk_ip_value('127001')
    assert not server._chk_ip_value('string_by_mistake')
    assert not server._chk_ip_value('335.0.0.l')
    assert not server._chk_ip_value('0.127.0.l')
    assert not server._chk_ip_value('127,0,0,l')


def test_chk_port_value():
    assert server._chk_port_value(7777)
    assert not server._chk_port_value('asd')
    assert not server._chk_port_value(80)
    assert not server._chk_port_value(808080)


class TestServer:
    # def setup_class(cls):
    #     print("basic setup into class")
    #
    # def teardown_class(cls):
    #     print("basic teardown into class")



    def test_chk_fields(self):
        x = server.Server('127.0.0.1', 7777)
        messages = [{'time': time.time(), 'login': 'max'},
                    {'action': 'presence', 't1me': time.time(), 'login': 'max'},
                    {'action': 'presence_might_to_be_alive_forever', 'time': time.time(), 'login': 'max'}
                    ]
        for message in messages:
            assert not x.chk_fields(message)

        assert x.chk_fields({'action': 'presence', 'time': time.time(), 'login': 'max'})
        del x

    def test_create_response(self):
        x = server.Server('127.0.0.1', 7777)
        values = [('200', {'new_key':'new_value'}), ('400', {'another_key':123})]
        good_responses = [{'response': '200', 'time': 'time'},
                          {'response': '200', 'time': 'time', 'new_key':'new_value'},
                          {'response': '400', 'time': 'time', 'another_key':123}
                          ]
        for value in values:
            response = x.create_response(value[0], **value[1])
            assert response in good_responses
        del x

    def test_prepare_connection(self):
        x = server.Server('127.0.0.1', 7777)
        assert type(x.server_socket) is socket.socket
        del x

    def test_dict_to_bytes_and_bytes_to_dict(self):#todo it's nesessary to change this test and start test send/recieve instead of encode/decode
        x = server.Server('127.0.0.1', 7777)
        messages = [
            {'response': '200', 'time': 'time'},
            {'response': '200', 'time': 'time', 'new_key':'new_value'},
            {'response': '400', 'time': 'time', 'another_key': 123}
        ]
        for message in messages:
            b = server._dict_to_bytes(message)
            d = server._bytes_to_dict(b)
            assert d == message
        del x

