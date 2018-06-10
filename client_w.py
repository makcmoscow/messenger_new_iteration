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
    def __init__(self, addr, port, account_name=None, password=None, user_name='guest'):
        self.addr = addr
        self.port = port
        self.sock = socket()
        self.account_name = str(account_name)
        self.password = str(password)
        self.user_name = str(user_name)

    def connect(self):
        self.sock.connect((self.addr, self.port))

    def send_message(self, message):
        b_message = _dict_to_bytes(message)
        self.sock.send(b_message)

    def get_message(self):
        b_message = self.sock.recv(1024)
        message = _bytes_to_dict(b_message)
        return message

    def mainloop_r(self):
        while True:
            message = self.get_message()
            print(message)

    def mainloop_w(self):
        while True:
            message = JIMmessage(self, text = input('Введите ваше сообщение: \n')).msg()

            self.send_message(message)

def handshake(client):
    presence = JIMmessage(client).presence()
    client.send_message(presence)
    s_response = client.get_message()
    return chk_response(s_response)

def chk_response(s_response):
    if s_response['response'] == '200':
        print('Everything well')
        return True
    else:
        print('there are error number {}'.format(s_response['response']))
        return False




class JIMmessage():
    def __init__(self, client, msg_type=None, text=None, to=None):

        self.time = str(time.ctime())
        self.type = str(msg_type)
        self.text = str(text)
        self.to = str(to)
        self.client = client

    def presence(self):
        presence = {
            'action': 'presence',
            'time': self.time,
            'type': self.type,
            'user': {
                'account_name': self.client.account_name,
                'status': 'OK'
            }
        }
        return presence

    def auth(self):
        auth_message = {
            'action': 'authenticate',
            'time': self.time,
            'user': {
                'account_name': self.client.account_name,
                'password': self.client.password
            }
        }
        return auth_message

    def msg(self):
        msg = {
            'action': 'msg',
            'time': self.time,
            'to': self.to,
            'from': self.client.account_name,
            'encoding': 'utf-8',
            'message': self.text
        }
        return msg

    # def join(self):
    #     join_chat = {
    #         'action': 'join',
    #         'time': time.time(),
    #         'room': '#room_name'
    #     }
    #     return join_chat

    # def leave(self):
    #     leave_chat = {
    #         'action': 'leave',
    #         'time': time.time(),
    #         'room': '#room_name'
    #     }
    #     return leave_chat

    def quit(self):
        quit = {
            'action': 'quit'
        }
        return quit

    def probe(self):
        probe = {
            'action': 'probe',
            'time': self.time
        }
        return probe

    # def alert(self, number, text):
    #     alert = {
    #         'response': number,
    #         'time': self.time,
    #         'alert': text
    #     }
    #     return alert

    # def error(self, number, text):
    #     error = {
    #         'response': number,
    #         'time': time.time(),
    #         'error': text
    #     }
    #     return error

    code = {
        '100': 'based notification',
        '101': 'important notice',
        '200': 'OK',
        '201': 'created',
        '202': 'accepted',

        '400': 'incorrect json object',
        '401': 'not authorized',
        '402': 'incorrect login or password',
        '403': 'user forbidden',
        '404': 'user or chat not found in server',
        '409': 'conflict! login is already in use',
        '410': 'user offline',
        '500': 'server error'
    }

def start():
    addr, port = parser()
    client = Client(addr, port)
    client.connect()
    # mode = input('Введите режим работы: {} или {}: '.format('r', 'w'))
    mode = 'w'
    client.user_name = input('Введите Ваше имя: ')
    if handshake(client):
        if mode == 'r':
            client.mainloop_r()
        else:
            client.mainloop_w()
    else:
        print('Something happened')



if __name__ == '__main__':
    start()