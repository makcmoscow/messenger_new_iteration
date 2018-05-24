from socket import *
import time
import json
import argparse
from common import _chk_ip_value, _chk_port_value, _dict_to_bytes, _bytes_to_dict

def parser(): #It returns IP address and port if they are was given
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', help='use this option to choose IP for listening')
    parser.add_argument('-p', '--port', help='use this option to choose server port')
    args = parser.parse_args()
    addr = '127.0.0.1'
    port = 7777
    if args.port and _chk_port_value(args.port): port = int(args.port)
    if args.addr and _chk_ip_value(args.addr): addr = args.addr
    return addr, port


class Client:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.sock = socket()

    def connect(self):
        self.sock.connect((self.addr ,self.port))

    def create_presence(self, **kwargs):
        presence = {'action': 'presence',
                    'time': time.time(),
                    'login': 'max'
                    }
        for key, value in kwargs.items(): #to put actual login or any additional information we'll use the kwargs
            presence[key] = value
        return presence


    def send_message(self, message):
        b_message = _dict_to_bytes(message)
        self.sock.send(b_message)

    def get_message(self):
        b_message = self.sock.recv(1024)
        message = _bytes_to_dict(b_message)
        return message

if __name__ == '__main__':
    addr, port = parser()
    client = Client(addr, port)
    client.connect()
    presence = client.create_presence()
    client.send_message(presence)
    s_response = client.get_message()
    if s_response['response'] == '200':
        print('Everything well')
    else:
        print('there are error number {}'.format(s_response['response']))
    print(s_response)