import sys
import os
import socket
from shutil import rmtree
from threading import Thread
from time import sleep


def init():
    try:
        rmtree(storage_name)  # todo
    except IOError:
        pass
    os.mkdir(storage_name)
    return '1'


def confirm_write(file_name, file_size):
    sock = socket.socket()
    sock.connect((name_server_ip, name_server_port))
    sock.sendall(str.encode("\n".join(['r', file_name, file_size])))
    sock.close()


"""def replicate(file_name, storage_list):
    for storage_info in storage_list:
        send_update_to_storage(file_name, storage_info[0], storage_info[1])"""


def send_file(file_name, sock):
    res = '0'
    try:
        with open(storage_name + '/' + file_name, 'rb') as f:
            file_size = os.fstat(f.fileno()).st_size
            sock.send(str.encode(str(file_size), 'utf-8'))
            l = f.read(chunk_size)
            while l:
                sock.send(l)
                l = f.read(chunk_size)
        res = '1'
    except:
        print("something went wrong with transmitting")
    return res


def write_file(file_name, file_size, sock):
    with open(storage_name + '/' + file_name, 'wb') as f:
        while True:
            data = sock.recv(chunk_size)
            if not data:
                if int(file_size) == os.fstat(f.fileno()).st_size:
                    return '1', file_size
                else:
                    return '0', file_size
            f.write(data)


def create(file_name):
    try:
        open(storage_name + '/' + file_name, 'w')
        return '1'
    except IOError:
        return '0'


def delete(file_name):
    try:
        os.remove(file_name)
        return '1'
    except IOError:
        return '0'


class ClientListener(Thread):
    def __init__(self, sock: socket.socket, addr):
        super().__init__(daemon=True)
        self.sock = sock
        self.addr = addr

    def _close(self):
        # users.remove(self.sock)
        # self.sock.shutdown(how=socket.SHUT_RDWR)
        print(self.name + ' disconnected.')
        self.sock.close()

    def run(self):
        command = self.sock.recv(2048).decode('utf-8').split('\n')
        args = command[1:]
        command = command[0]
        res = '0'
        try:
            if command == 'c':
                res = create(args[0])
                confirm_write(args[0], '0')

            elif command == 'r':
                for _ in args[1:]:
                    res = send_file(args[0], self.sock)
                """f = open(file_name)
                data = f.read()
                res = data"""

            elif command == 'w':
                res, f_size = write_file(args[0], args[1], self.sock)
                # initialize_replica(file_name)
                self.sock.sendall(str.encode("\n".join(res)))
                confirm_write(args[0], f_size)

            elif command == 'd':
                res = delete(args[0])
                # self.sock.sendall(str.encode("\n".join(res)))

            """elif command == 'replicate':
                file_name = args[0]
                storage_info = args[1:]
                replicate(file_name, storage_info)
                res = 1"""
        except:
            self.sock.sendall(str.encode("\n".join(res)))

        self._close()


class Heart(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_alive = True
        self.heartbeat_time = 2
        self.sock.settimeout(self.heartbeat_time + 1)

    def _close(self):
        # self.sock.shutdown(how=socket.SHUT_RDWR)
        self.sock.close()

    def run(self):
        try:
            self.sock.connect((name_server_ip, name_server_port))
            self.sock.send(str.encode('hello'))
            while True:
                sleep(self.heartbeat_time)
                self.sock.send(str.encode("1"))
        except:
            self.is_alive = False
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, guest_port))
            self._close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        name_server_ip = sys.argv[1]
    else:
        name_server_ip = '172.21.0.2'  # TODO
    name_server_port = 19609
    guest_port = 12607
    host = ''
    storage_name = 'storage'
    chunk_size = 1024

    heart = Heart()
    heart.start()

    init()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, guest_port))

    sock.listen()
    while heart.is_alive:
        con, addr = sock.accept()
        # start new thread for user
        ClientListener(con, addr).start()
