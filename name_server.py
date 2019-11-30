import socket
import xml.etree.ElementTree as ET
from threading import Thread


def create_root():
    root = ET.Element("root")
    tree = ET.ElementTree(root)
    tree.write(root_filename)
    return tree


def welcome_user(ip, port, name):
    users.append({
        'ip': ip,
        'port': port,
        'name': name
    })


def get_node(user, path):
    xml_path = './user[@name="%s"]' % user
    for d in path.split('\\'):
        xml_path += '/d[@name="%s"]' % d
    return root.find(xml_path)
    # return root.find('./%s/%s' % (user, path))


def get_file(user, path: str):
    file_begins_at = path.rfind('\\')
    node = get_node(user, path[:file_begins_at]) if file_begins_at != -1 else get_node(user, "")
    return node.find('./f[@name="%s"]' % path[file_begins_at+1:])


class ClientListener(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = ""

    # clean up
    def _close(self):
        # users.remove(self.sock)
        # self.sock.shutdown(how=socket.SHUT_RDWR)
        self.sock.close()
        print(self.name + ' disconnected.')

    def run(self):
        self.name = self.sock.recv(1024).decode("utf-8")
        # welcome_user(self.addr[0], self.addr[1], self.name)
        print("Hi, %s!" % self.name)
        # all command receiving should be here
        self._close()


if __name__ == "__main__":
    host = ''
    port = 8800
    root_filename = 'root.xml'

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))

    users = []  # maybe remove? don't see the purpose
    banks = []
    # TODO find/lift banks?
    try:
        tree = ET.parse(root_filename)
    except IOError:
        tree = create_root()
    root = tree.getroot()
    # el = get_file("mydude", "Wonderful.png")

    sock.listen()
    while True:
        con, addr = sock.accept()
        # start new thread for user
        ClientListener(con).start()
