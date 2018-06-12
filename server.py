from socket import *
import argparse
import json
import time
import select
from common import _chk_ip_value, _chk_port_value
from logger import logger
from json.decoder import JSONDecodeError
from queue import Queue

class JIMresponse:
    def __init__(self, code):
        self.code = code
        self.time = time.time()
        self.code_dict = {
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

    def response(self):
        response = {
            'response': self.code,
            'time': self.time,
            'alert': self.code_dict[self.code]
        }
        return response


class JIMmessage:
    def __init__(self):
        self.actions = {'probe': self.probe}
        self.time = time.time()

    def probe(self):
        probe = {
            'action': 'probe',
            'time': self.time
        }
        return probe

@logger
def parser():  # It returns IP address and port if they are was given
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', help='use this option to choose IP for listening')
    parser.add_argument('-p', '--port', help='use this option to choose server port')
    args = parser.parse_args()
    addr = ''
    port = 7777
    if args.port and _chk_port_value(args.port): port = int(args.port)
    if args.addr and _chk_ip_value(args.addr): addr = args.addr
    return addr, port


class Client():
    def __init__(self, socket):
        self.socket = socket


class Server:
    def __init__(self, addr, port):
        self.addr = addr  # IP used to client's connect, default = any available
        self.port = port  # port used to client's connect, default = 7777
        self.server_socket = self.prepare_connection()  # socket for client connections
        self.all_clients = {}
        self.all_clients_socks = []
        self.readers = []
        self.writers = []

    def prepare_connection(self, timeout=0.2):  # Let's prepare server socket for job
        server_socket = socket()
        server_socket.bind((self.addr, self.port))
        server_socket.listen()
        server_socket.settimeout(timeout)
        return server_socket
    @logger
    def send_message(self, message, socket):  # This function need dict message and client socket
        try:
            b_message = self._dict_to_bytes(message)
            socket.send(b_message)
        except ConnectionResetError:
            print('Клиент отключился')
            socket.close()
            self.all_clients_socks.remove(socket) if socket in self.all_clients_socks else None
            self.all_clients.pop(socket) if socket in self.all_clients else None
        except OSError:
            pass

    @logger
    def get_message(self, socket):  # This function need client socket and returns dict message
        try:
            b_message = socket.recv(1024)
            message = self._bytes_to_dict(b_message)
            return message
        except ConnectionResetError:
            self.all_clients_socks.remove(socket) if socket in self.all_clients_socks else None
            self.all_clients.pop(socket) if socket in self.all_clients else None
            print('Клиент отключился и был удален')
        except OSError:
            pass


    @logger
    def chk_fields(self, message):
        if 'action' in message and 'time' in message and (len(message['action']) < 15):
            return '200'
        else:
            return '400'
    @logger
    def create_response(self, *args, **kwargs):
        response = {'response': args[0], 'time': 'time'}  # first argument supposed to be code server's response
        for key, value in kwargs.items():  # if we need to create special responce, we just give kwargs dictionary.
            response[key] = value
        return response
    @logger
    def _dict_to_bytes(self, message):
        j_message = json.dumps(message)
        b_message = j_message.encode()
        return b_message
    @logger
    def _bytes_to_dict(self, b_message):
        try:
            j_message = b_message.decode()
            message = json.loads(j_message)
        except JSONDecodeError:
            message = {}
        return message
    @logger
    def message_handler(self, socket):
        request = self.get_message(socket)
        if request:
            code = self.chk_fields(request)
            response = JIMresponse(code).response()
            self.send_message(response, socket)
            # return request

    def mainloop(self):


        while True:
            try:
                client_sock, address = self.server_socket.accept()
                client = Client(client_sock)
                self.message_handler(client.socket)
            except OSError:
                pass
            else:
                self.all_clients_socks.append(client.socket)
                self.all_clients[client_sock] = client
                print(self.all_clients)
            finally:
                try:
                    self.writers, self.readers, self.errors = select.select(self.all_clients_socks, self.all_clients_socks, [])
                except Exception as e:
                    pass

                requests = []
                for writer in self.writers:
                    # request = self.message_handler(writer)
                    request = self.get_message(writer)
                    if request and request['action'] == 'msg':
                        requests.append(request)
                    # self.message_handler(writer)
                for reader in self.readers:
                    for request in requests:
                        self.send_message(request, reader)


if __name__ == '__main__':
    addr, port = parser()
    server = Server(addr, port)
    server.mainloop()


