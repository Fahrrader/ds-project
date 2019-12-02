import os
import socket
from threading import Thread
from time import sleep


def initialize_replica(file_name):
    sock = socket.socket()
    sock.connect((name_server_ip, name_server_port))
    sock.sendall(str.encode("\n".join(['replicate', file_name])))
    sock.close()


def replicate(file_name, storage_list):
    for storage_info in storage_list:
        send_update_to_storage(file_name, storage_info[0], storage_info[1])


def send_update_to_storage(file_name, storage_port, storage_ip):
    sock = socket.socket()
    sock.connect((storage_ip, storage_port))
    sock.sendall(str.encode("\n".join(['w', file_name])))
    result = sock.recv(2048).decode('utf-8').split('\n')
    if result == '1':
        print("The file has been successfully replicated.")


def create_file(file_name):
    pass


def edit_file(file_name, new_data):
    try:
        f = open(file_name)
        f.write(new_data)
        res = '1'
    except:
        res = '0'


class clientListener(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock

    def _close(self):
        # users.remove(self.sock)
        # self.sock.shutdown(how=socket.SHUT_RDWR)
        print(self.name + ' disconnected.')
        self.sock.close()

    def run(self):
        command = self.sock.recv(2048).decode('utf-8').split('\n')
        args = command[1:]
        command = command[0]
        res = ''

        if command == 'r':
            file_name = args[0]
            f = open(file_name)
            data = f.read()
            res = data

        elif command == 'w':
            file_name = args[0]
            data = args[1:]
            res = edit_file(file_name, data)
            initialize_replica(file_name)


        elif command == 'd':
            file_name = args[0]
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), file_name)
            os.remove(path)
            res = '1'

        elif command == 'replicate':
            file_name = args[0]
            storage_info = args[1:]
            replicate(file_name, storage_info)
            res = 1

        self.sock.sendall(str.encode("\n".join(res)))
        self._close()


class heartbeat(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = ""

    def _close(self):
        # users.remove(self.sock)
        # self.sock.shutdown(how=socket.SHUT_RDWR)
        self.sock.close()
        print(self.name + ' disconnected.')

    def run(self):
        sleep(1)
        sock = socket.socket()
        sock.connect((name_server_port, name_server_port))
        sock.sendall(str.encode("1"))


if __name__ == "__main__":
    name_server_ip = 'localhost'  # TODO
    name_server_port = 9000
    host = ''
    guest_port = 8800


    name_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    name_sock.bind((host, guest_port))
    # heartbeat(con).start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, guest_port))

    sock.listen()
    while True:
        con, addr = sock.accept()
        # start new thread for user
        clientListener(con).start()
