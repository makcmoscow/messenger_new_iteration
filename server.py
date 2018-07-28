from socket import *
import argparse
import json
import time
import select
import Table_handler
from common import _chk_ip_value, _chk_port_value
from logger import logger
from json.decoder import JSONDecodeError
from multiprocessing import Queue
import datetime
import asyncio

q_messages = Queue()

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
        self.last_send_time = None
        self.nickname = None
        self.password = None
        self.login_name = None
        self.address = None


    def is_registered(self):
        is_user = Table_handler.User().get_user(login_name=self.login_name)
        if not is_user:
            print('Похоже, что к нам подключился совершенно новый пользователь, нужно его занести в базу')
            return False
            #Запросили, и теперь мы можем добавить его в базу
        if is_user:
            return True

    def registration(self):
        if not self.nickname: self.nickname = self.login_name
        new_user = Table_handler.User(login_name = self.login_name, nickname=self.nickname, password=self.password)
        new_user.add_user()
        print('Мы успешно зарегистрировали клиента! никнейм: {}, пароль: {}'.format(self.nickname, self.password))

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

    def set_last_exit_time(self, socket):
        instance = Table_handler.History()
        user_login = self.all_clients[socket].login_name
        user_history = Table_handler.History().get_user_hystory(
            login_name=user_login)
        last_enter_time = user_history.last_enter_time
        last_ip_address = user_history.last_ip_address
        instance.del_user_history(user_login)
        Table_handler.History(login_name=user_login,
                              last_ip_address=last_ip_address,
                              last_exit_time=time.time(),
                              last_enter_time=last_enter_time).add_user_history()


    def send_message(self, message, socket):  # This function need dict message and client socket
        try:
            b_message = self._dict_to_bytes(message)
            socket.send(b_message)
        except ConnectionResetError:
            print('Клиент отключился')
            self.set_last_exit_time(socket)
            socket.close()
            self.all_clients_socks.remove(socket) if socket in self.all_clients_socks else None
            self.all_clients.pop(socket) if socket in self.all_clients else None
        except OSError:
            pass


    def get_message(self, socket):  # This function need client socket and returns dict message
        try:
            b_message = socket.recv(1024)
            message = self._bytes_to_dict(b_message)
            return message
        except ConnectionResetError:
            self.set_last_exit_time(socket)
            self.all_clients_socks.remove(socket) if socket in self.all_clients_socks else None
            self.all_clients.pop(socket) if socket in self.all_clients else None
            self.writers.remove(socket) if socket in self.writers else None
            self.readers.remove(socket) if socket in self.readers else None
            print('Клиент отключился и был удален')
        except OSError:
            pass



    def chk_fields(self, message):
        if 'action' in message and 'time' in message and (len(message['action']) < 15):
            return '200'
        else:
            return '400'


    def _dict_to_bytes(self, message):
        j_message = json.dumps(message)
        b_message = j_message.encode()
        return b_message

    def _bytes_to_dict(self, b_message):
        try:
            j_message = b_message.decode()
            message = json.loads(j_message)
        except JSONDecodeError:
            message = {}
        return message

    def handshake(self, socket): # handshake
        request = self.get_message(socket)
        if request:
            code = self.chk_fields(request)
            response = JIMresponse(code).response()
            self.send_message(response, socket)
            user_login_name = request['user']['login_name']

            return user_login_name, True
        else:
            return None, False





    def authenticate(self, client):
        request = self.get_message(client.socket)
        if request:
            client.password = request['user']['password']
            if client.is_registered():
                print('К нам подключился зарегистрированный пользователь')
                code = self.chk_fields(request)
                response = JIMresponse(code).response()
                self.send_message(response, client.socket)
                return True
            else:
                print('К нам подключился незарегистрированный пользователь')
                # client.registration()
                message = JIMresponse('404')
                message = message.response()
                self.send_message(message, client.socket)
                return False








    def accepting(self):
        client_sock, address = self.server_socket.accept()
        client = Client(client_sock)
        client.address = address
        return client

    def update_user_history(self, client):
        user = Table_handler.User().get_user(
            login_name=client.login_name)
        user_history = Table_handler.History().get_user_hystory(
            login_name=user.login_name)
        if user_history:
            last_enter_time = user_history.last_enter_time
            last_exit_time = user_history.last_exit_time
            last_ip_address = user_history.last_ip_address
            Table_handler.History(login_name=user.login_name,
                                  last_ip_address=last_ip_address,
                                  last_exit_time=last_exit_time,
                                  last_enter_time=last_enter_time).add_user_history()
        else:
            Table_handler.History(login_name=user.login_name,
                                  last_ip_address=client.address[0],
                                  last_enter_time=time.time()).add_user_history()


    async def writers_loop(self):
        while True:
            for writer in self.writers:
                request = self.get_message(writer)
                if request and request['action'] == 'msg':
                    q_messages.put(request)
            await asyncio.sleep(0)
    async  def readers_loop(self):
        while True:
            if q_messages.empty():
                pass
            else:
                request = q_messages.get()
                for reader in self.readers:
                    print('request', request)
                    if request['to'] == self.all_clients[reader].login_name:
                        self.send_message(request, reader)

            await asyncio.sleep(0)

    async def mainloop(self):
        while True:
            try:
                client = self.accepting()
            except OSError:
                pass
            else:
                client.login_name, handshake_well = self.handshake(client.socket)
                if handshake_well:
                    if self.authenticate(client):
                        self.update_user_history(client)
                        self.all_clients_socks.append(client.socket)
                        self.all_clients[client.socket] = client
                        print(self.all_clients)
                    else:
                        print('незарегистрированный клиент ушел на хуй')
                else:
                    print('handshake wrong')
            finally:
                try:
                    self.writers, self.readers, self.errors = select.select(self.all_clients_socks, self.all_clients_socks, [])
                except Exception as e:
                    pass
            await asyncio.sleep(0)

                # requests = []




if __name__ == '__main__':
    addr, port = parser()
    server = Server(addr, port)

    ioloop = asyncio.get_event_loop()
    tasks = [ioloop.create_task(server.mainloop()), ioloop.create_task(server.readers_loop()), ioloop.create_task(server.writers_loop())]
    wait_tasks = asyncio.wait(tasks)
    ioloop.run_until_complete(wait_tasks)
    ioloop.close()


    server.mainloop()


