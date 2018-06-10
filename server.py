from socket import *
import sys
import argparse
import json
import time
import select
from common import _chk_ip_value, _chk_port_value
from logger import logger
from queue import Queue

class JIMmessage:
    def __init__(self):
        pass




def parser(): #It returns IP address and port if they are was given
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
        self.addr = addr #IP used to client's connect, default = any available
        self.port = port#port used to client's connect, default = 7777
        self.server_socket = self.prepare_connection()#socket for client connections
        self.all_clients = {}

    def prepare_connection(self, timeout = 0.2):# Let's prepare server socket for job
        server_socket = socket()
        server_socket.bind((self.addr, self.port))
        server_socket.listen()
        server_socket.settimeout(timeout)
        return server_socket
    @logger
    def send_message(self, message, socket):# This function need dict message and client socket
        try:
            b_message = self._dict_to_bytes(message)
            socket.send(b_message)
        except OSError:
            print('Клиент отключился')
            socket.close()
            self.all_clients_socks.remove(socket)
            self.all_clients.pop(socket)


    @logger
    def get_message(self, socket):# This function need client socket and returns dict message
        try:
            b_message = socket.recv(1024)
            message = self._bytes_to_dict(b_message)
            return message
        except OSError:
            self.all_clients_socks.remove(socket)
            self.all_clients.pop(socket)



    def chk_fields(self, message):
        if 'action' in message and 'time' in message and (len(message['action']) < 15):
            return True
        else:
            return False

    def create_response(self, *args, **kwargs):
        response = {'response': args[0], 'time': 'time'} #first argument supposed to be code server's response
        for key, value in kwargs.items():#if we need to create special responce, we just give kwargs dictionary.
            response[key] = value
        print(response)
        return response

    def _dict_to_bytes(self, message):
        j_message = json.dumps(message)
        b_message = j_message.encode()
        return b_message

    def _bytes_to_dict(self, b_message):
        j_message = b_message.decode()
        message = json.loads(j_message)
        return message

    def presence_handler(self, new_client):
        request = self.get_message(new_client.socket)
        if self.chk_fields(request):
            response = self.create_response('200', time=time.time())
        else:
            response = self.create_response('400', time=time.time())
        self.send_message(response, new_client.socket)


    def mainloop(self):
        self.all_clients_socks = []
        self.readers = []
        self.writers = []

        while True:
            try:
                client_sock, address = self.server_socket.accept()
                client = Client(client_sock)
                self.presence_handler(client)
            except OSError:
                pass
            else:
                self.all_clients_socks.append(client.socket)
                self.all_clients[client_sock] = client
            finally:
                try:
                    self.writers, self.readers, self.errors = select.select(self.all_clients_socks, self.all_clients_socks, [])
                except Exception as e:
                    pass

                requests = []
                responces = []
                for writer in self.writers:
                    request = self.get_message(writer)
                    print(request)
                    requests.append(request)
                for reader in self.readers:
                    for request in requests:
                        print(request)
                        self.send_message(request, reader)



                # try:
                #     incoming_message = self.get_messages()
                #     if self.chk_fields(incoming_message):
                #         response = self.create_response('200', time = time.time())
                #     else:
                #         response = self.create_response('400', time = time.time())
                #     self.send_messages(response)
                #     sys.exit(0)
                # except OSError:
                #     pass


if __name__ == '__main__':
    addr, port = parser()
    server = Server(addr, port)
    server.mainloop()