from socket import *
import time
import json
import argparse

# def parser():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--addr', help='use this option to choose server IP')
#     parser.add_argument('-p', '--port', help='use this option to choose server port')
#     args = parser.parse_args()
#     addr = '127.0.0.1'
#     port = 7777
#     if args.port: port = int(args.port)
#     if args.addr: addr = args.addr
#     return addr, port
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


def _chk_ip_value(value):
    err_text = 'IP address supposed to be 4 integer number separated by ".", not {}'
    test_value = value.split('.')
    if len(test_value) != 4:
        print(err_text.format(value))
    else:
        for x in test_value:
            try:
                x = int(x)
            except ValueError:
                print(err_text.format(value))
                return False
            else:
                if int(x) < 0 or int(x) > 254:
                    print(err_text.format(value))
                    return False
        return True


def _chk_port_value(value):
    try:
        port = int(value)
    except ValueError:
        print('Port supposed to be integer value, not {}. Now we are using 7777'.format(port))
        return False
    else:
        if port > 65534 or port < 1024:
            print('Port supposed to be between 1024 and 65535, not {}. Now we are using 7777'.format(port))
            return False
        else:
            return True


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
        for key, value in kwargs: #to put actual login or any additional information we'll use the kwargs
            presence[key] = value
        return presence

    def dict_to_bytes(self, message):
        j_message = json.dumps(message)
        b_message = j_message.encode()
        return b_message

    def bytes_to_dict(self, b_message):
        j_message = b_message.decode()
        message = json.loads(j_message)
        return message

    def send_message(self, message):
        b_message = self.dict_to_bytes(message)
        self.sock.send(b_message)

    def get_message(self):
        b_message = self.sock.recv(1024)
        message = self.bytes_to_dict(b_message)
        return message

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

