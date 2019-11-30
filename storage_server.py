import socket
from threading import Thread
import os
import webbrowser
from time import sleep
import socket

class clientListener(Thread):
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
        # command = [i for i in self.sock.recv(2048).decode('utf-8').split('\n')]
        command = self.sock.recv(2048).decode('utf-8').split('\n')
        res = ''

        if command == 'r':
            pass

        elif command == 'w':
            pass

        elif command == 'd':
            pass

        elif command == 'replicate':
            pass

        self.sock.sendall(str.encode("\n".join(res)))

        # welcome_user(self.addr[0], self.addr[1], self.name)
        # print("Hi, %s!" % self.name)
        # TODO all command receiving should be here
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
        server_ip = 'localhost'  #TODO
        port = 8800
        sleep(1)
        sock = socket.socket()
        sock.connect((server_ip, port))
        sock.sendall(str.encode("1"))


if __name__ == "__main__":
    name_server_ip = 'localhost'  # TODO
    name_server_port = 8800
    host = ''

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, name_server_port))

    sock.listen()
    while True:
        con, addr = sock.accept()
        # start new thread for user
        clientListener(con).start()
        heartbeat(con).start()
