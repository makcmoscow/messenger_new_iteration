from socket import *
import sys
import time
import argparse
import json
import time

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', help='use this option to choose IP for listen')
    parser.add_argument('-p', '--port', help='use this option to choose server port')
    args = parser.parse_args()
    addr = '127.0.0.1'
    port = 7777
    if args.port: port = args.port
    if args.addr: addr = args.addr
    return addr, port

class Client():
    def __init__(self, socket):
        self.socket = socket


class Server:
    def __init__(self, addr, port):
        self.addr = addr #IP used to client's connect, default = 127.0.0.1
        self.port = port#port used to client's connect, default = 7777
        self.serv_socket = self.prepare_connection()#socket for client connections

    def prepare_connection(self):
        serv_socket = socket()
        serv_socket.bind((self.addr, self.port))
        serv_socket.listen()
        serv_socket.settimeout(10)
        return serv_socket

    def send_message(self, message, socket):
        b_message = self._dict_to_bytes(message)
        socket.send(b_message)

    def get_message(self, socket):
        b_message = socket.recv(1024)
        message = self._bytes_to_dict(b_message)
        return message


    def chk_fields(self, message):
        if 'action' in message and 'time' in message and (len(message['action'])<15):
            return True
        else:
            return False

    def create_response(self, *args, **kwargs):
        response = {'response': None, 'time': None}
        response['response'] = args[0] #first argument supposed to be code server's response
        response['time'] = time.time()
        for key, value in kwargs:#if we need to create special responce, we just give kwargs dictionary.
            response[key] = value
        return response

    def _dict_to_bytes(self, message):
        j_message = json.dumps(message)
        b_message = j_message.encode()
        return b_message

    def _bytes_to_dict(self, b_message):
        j_message = b_message.decode()
        message = json.loads(j_message)
        return message


    def mainloop(self):
        while True:
            try:
                client_sock, addr = self.serv_socket.accept()
                client = Client(client_sock)
            except OSError:
                pass
            else:
                try:
                    incoming_message = self.get_message(client.socket)
                    if self.chk_fields(incoming_message):
                        response = self.create_response('200')
                    else:
                        response = self.create_response('400')
                    self.send_message(response, client.socket)
                    sys.exit(0)
                except OSError:
                    pass
            finally:
                self.mainloop()


addr, port = parser()
server = Server(addr, port)
server.mainloop()



