from socket import *
import sys
import argparse
import json
import time


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


def _chk_ip_value(value):
    err_text = 'IP address supposed to be 4 integer number separated by ".", not {}'
    test_value = value.split('.')
    if len(test_value) != 4:
        print(err_text.format(value))
    else:
        counter = 0
        for x in test_value:
            try:
                x = int(x)
                if x == 0 and counter == 0:
                    print('IP address couldn\'t be started of zero')
                    return False
            except ValueError:
                print(err_text.format(value))
                return False
            else:
                if int(x) < 0 or int(x) > 254:
                    print(err_text.format(value))
                    return False
                counter += 1
        return True


def _chk_port_value(value):
    try:
        port = int(value)
    except ValueError:
        print('Port supposed to be integer value, not {}. Now we\'ll use 7777'.format(value))
        return False
    else:
        if port > 65534 or port < 1024:
            print('Port supposed to be between 1024 and 65535, not {}. Now we\'ll use 7777'.format(value))
            return False
        else:
            return True


class Client():
    def __init__(self, socket):
        self.socket = socket


class Server:
    def __init__(self, addr, port):
        self.addr = addr #IP used to client's connect, default = any available
        self.port = port#port used to client's connect, default = 7777
        self.server_socket = self.prepare_connection()#socket for client connections

    def prepare_connection(self, timeout = 10):# Let's prepare server socket for job
        server_socket = socket()
        server_socket.bind((self.addr, self.port))
        server_socket.listen()
        server_socket.settimeout(timeout)
        return server_socket

    def send_message(self, message, sock):# This function need dict message and client socket
        b_message = self._dict_to_bytes(message)
        sock.send(b_message)

    def get_message(self, sock):# This function need client socket and returns dict message
        b_message = sock.recv(1024)
        message = self._bytes_to_dict(b_message)
        return message


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


    def mainloop(self):
        while True:
            try:
                client_sock, address = self.server_socket.accept()
                client = Client(client_sock)
            except OSError:
                pass
            else:
                try:
                    incoming_message = self.get_message(client.socket)
                    if self.chk_fields(incoming_message):
                        response = self.create_response('200', time = time.time())
                    else:
                        response = self.create_response('400', time = time.time())
                    self.send_message(response, client.socket)
                    sys.exit(0)
                except OSError:
                    pass
            finally:
                self.mainloop()

if __name__ == '__main__':
    addr, port = parser()
    server = Server(addr, port)
    server.mainloop()