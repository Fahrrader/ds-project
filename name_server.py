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
    if path.strip() != "":
        for d in path.split('\\'):
            xml_path += '/d[@name="%s"]' % d
    return root.find(xml_path)
    # return root.find('./%s/%s' % (user, path))


def get_last_node_split(path: str):
    file_begins_at = path.rfind('\\')
    return path[:file_begins_at] if file_begins_at != -1 else "", file_begins_at


def get_file(user, path: str):
    cut_path, file_begins_at = get_last_node_split(path)
    # print(cut_path, file_begins_at)
    node = get_node(user, cut_path)
    return node.find('./f[@name="%s"]' % path[file_begins_at+1:]) if node is not None else None


# TODO return codes? like done, already exists, no such pathway
def make_dir(user, path):
    cut_path, new_dir_begins_at = get_last_node_split(path)
    new_dir = path[new_dir_begins_at+1:]
    node = get_node(user, cut_path)
    if node is None:
        return '0'
    if node.find('./d[@name="%s"]' % new_dir) is not None:
        return '2'
    dir_node = ET.SubElement(node, 'd')
    dir_node.set('name', new_dir)
    tree.write(root_filename)
    return '1'


def delete_dir(user, path):
    cut_path, dir_begins_at = get_last_node_split(path)
    node = get_node(user, cut_path)  # cut_path)
    if node is None:
        return 0
    deleted = node.find('./d[@name="%s"]' % path[dir_begins_at + 1:])
    if deleted is None:
        return 2
    node.remove(deleted)
    tree.write(root_filename)
    return 1


def check_for_dir(user, path):
    """used for change directory"""
    node = get_node(user, path)
    return '1' if node is not None else '2'


def list_dir(user, path):
    node = get_node(user, path)
    if node is None:
        return []
    listed = []
    for el in node:
        listed.append(el.tag + ': ' + el.attrib["name"])
    return listed


def init(user):
    user_node = get_node(user, "")
    if user_node is not None:
        root.remove(user_node)
    user_node = ET.SubElement(root, 'user')
    user_node.set('name', user)
    tree.write(root_filename)
    return '1'


# def create_file(user, path):


class ClientListener(Thread):
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
        # name, command = [i for i in self.sock.recv(2048).decode('utf-8').split('\n')]
        args = self.sock.recv(2048).decode('utf-8').split('\n')
        name = args[0]
        command = args[1]
        print(name, command)
        self.name = name
        res = '0'

        if command == 'init':
            res = init(name)
        elif command == 'c':
            pass
        elif command == 'r':
            pass

        elif command == 'w':
            pass

        elif command == 'd':
            # TODO func for both files and directories
            pass

        elif command == 'i':
            pass

        elif command == 'cp':
            pass

        elif command == 'mv':
            pass

        elif command == 'cd':
            res = check_for_dir(name, args[2])
        elif command == 'ls':
            res = list_dir(name, args[2])
        elif command == 'md':
            res = make_dir(name, args[2])
        self.sock.sendall(str.encode("\n".join(res)))

        # welcome_user(self.addr[0], self.addr[1], self.name)
        # print("Hi, %s!" % self.name)
        # TODO all command receiving should be here
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
    # el = root.findall('.//*[@name="This is hay"]')
    # print(el)

    sock.listen()
    while True:
        con, addr = sock.accept()
        # start new thread for user
        ClientListener(con).start()
