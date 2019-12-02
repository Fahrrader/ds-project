import socket
import string
import xml.etree.ElementTree as ET
from threading import Thread
from random import choices
import time
import datetime


def create_root():
    root = ET.Element("root")
    tree = ET.ElementTree(root)
    tree.write(root_filename)
    return tree


def get_node(user, path):
    xml_path = './user[@name="%s"]' % user
    if path.strip() != "":
        for d in path.split('\\'):
            xml_path += '/d[@name="%s"]' % d
    return root.find(xml_path)
    # return root.find('./%s/%s' % (user, path))


def get_last_node_split(path: str):
    file_begins_at = path.rfind('\\')
    return path[:file_begins_at] if file_begins_at != -1 else "", path[file_begins_at + 1:]


def get_file(user, path: str):
    cut_path, file = get_last_node_split(path)
    # print(cut_path, file_begins_at)
    node = get_node(user, cut_path)
    return node.find('./f[@name="%s"]' % file) if node is not None else None, node


def make_dir(user, path):
    cut_path, new_dir = get_last_node_split(path)
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
    cut_path, del_dir = get_last_node_split(path)
    node = get_node(user, cut_path)
    if node is None:
        return '0'
    deleted = node.find('./d[@name="%s"]' % del_dir)
    if deleted is None:
        return '2'
    for _ in deleted:
        return '9'
    node.remove(deleted)
    tree.write(root_filename)
    return '1'


def finally_delete_dir(user, path):
    cut_path, del_dir = get_last_node_split(path)
    node = get_node(user, cut_path)
    if node is None:
        return '0'
    deleted = node.find('./d[@name="%s"]' % del_dir)
    if deleted is None:
        return '2'
    # TODO go through every single file in the node, delete
    # deleted.findall('.//f')
    node.remove(deleted)
    tree.write(root_filename)
    return '1'


def move_file(user, path, path2):
    # cut_path, dir_begins_at = get_last_node_split(path)
    file, node1 = get_file(user, path)
    if node1 is None:
        return '0'
    if file is None:
        return '2'
    _, file_path = get_last_node_split(path)
    file2, node2 = get_file(user, path2 + "\\" + file_path)
    if node2 is None:
        return '3'
    if file2 is not None:
        return '4'
    node2.append(file)
    node1.remove(file)
    tree.write(root_filename)
    return '1'


def copy_file(user, path, path2):
    # cut_path, dir_begins_at = get_last_node_split(path)
    file, node1 = get_file(user, path)
    if node1 is None:
        return '0'
    if file is None:
        return '2'
    _, file_path = get_last_node_split(path)
    file2, node2 = get_file(user, path2 + "\\" + file_path)
    if node2 is None:
        return '3'
    if file2 is not None:
        return '4'
    # node2.append(file)
    # tree.write(root_filename)
    _, file = get_last_node_split(path)
    return create_file(user, path2 + "\\" + file)  # TODO check for problems later, adjust registry


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


def create_file(user, path):
    file, node = get_file(user, path)
    if node is None:
        return '0'
    if file is not None:
        return '2'

    elements = ['']
    while elements:
        new_id = ''.join(choices(string.ascii_letters + string.digits, k=64))
        elements = root.findall('.//*[@id="%s"]' % new_id)
    # todo send one of the banks IP (the most free one, perhaps) and the file id
    # TODO after bank returns signal that the file is uploaded:
    # file id, size
    cut_path, file_name = get_last_node_split(path)
    file = ET.SubElement(node, 'f', attrib={
        'id': new_id,
        'name': file_name,
        'size': '0',  # something
        'created': str(datetime.datetime.now()),
        'modified': str(datetime.datetime.now())
    })
    # set text to already replicated server
    # TODO ping banks with other IPs for it to store the thing
    # each time update text to new replicated server
    # each time a server stops responding, find the files from the server,
    # run through formula and replicate somewhere else if need be
    # TODO also ping client that the upload is complete
    tree.write(root_filename)
    return '1'


def write_file(user, path):
    file, node = get_file(user, path)
    if node is None:
        return '0'
    if file is None:
        # return '2'
        elements = ['']
        while elements:
            file_id = ''.join(choices(string.ascii_letters + string.digits, k=64))
            elements = root.findall('.//*[@id="%s"]' % file_id)
    else:
        file_id = file.get('id')
    # TODO return IP, id

    if file is None:
        _, file_name = get_last_node_split(path)
        file = ET.SubElement(node, 'f', attrib={
            'id': file_id,
            'name': file_name,
            'size': '0',  # something
            'created': str(datetime.datetime.now()),
            'modified': str(datetime.datetime.now())
        })

    # wait for ack from bank
    file.set('modified', str(datetime.datetime.now()))
    file.set('size', '0')  # change
    return '1'


def get_bank(text):
    bank_indices = text.strip().split(',') if text is not None else []
    if not bank_indices:
        return '-1'
    bank = choices(bank_indices)[0]
    while not (bank in banks):
        bank = choices(bank_indices)[0]
    return bank


def read_file(user, path):
    file, node = get_file(user, path)
    if node is None:
        return '0'
    if file is None:
        return '2'

    file_id = file.get('id')
    bank = get_bank(file.text)
    if bank == '-1':
        delete_file(user, path)
        return '2'

    return [bank, file_id]


def delete_file(user, path):
    file, node = get_file(user, path)
    if node is None:
        return '0'
    if file is None:
        return '2'
    bank_indices = file.text.strip().split(',') if file.text is not None else []
    print(bank_indices)
    # TODO send to all banks commands to delete
    file.set('op', 'd')
    # TODO do the following ONLY AFTER every (functioning) replicant deletes
    node.remove(file)
    tree.write(root_filename)
    return '1'


def get_file_info(user, path):
    file, node = get_file(user, path)
    if node is None:
        return '0'
    if file is None:
        return '2'
    return [file.attrib['size'], file.attrib['created'], file.attrib['modified']]


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
        args = self.sock.recv(4096).decode('utf-8').split('\n')
        name = args[0]
        command = args[1]
        print(name + ' commands ' + command)
        self.name = name
        res = '0'

        # TODO
        """if not banks.keys():
            res = '0'"""
        if command == 'init':
            res = init(name)
        elif command == 'c':
            res = create_file(name, args[2])
        elif command == 'r':
            res = read_file(name, args[2])
            # to send back [storage_ip, storage_port, file_name]
        elif command == 'w':
            res = write_file(name, args[2])
            # to send back [storage_ip, storage_port, file_name]
        elif command == 'd':
            res = delete_file(name, args[2])
            # answer 0 if an error, 1 if okay, 2 if no such file
        elif command == 'i':
            res = get_file_info(name, args[2])
        elif command == 'cp':
            res = copy_file(name, args[2], args[3])
        elif command == 'mv':
            res = move_file(name, args[2], args[3])
        elif command == 'cd':
            res = check_for_dir(name, args[2])
        elif command == 'ls':
            res = list_dir(name, args[2])
        elif command == 'md':
            res = make_dir(name, args[2])
        elif command == 'dd':
            if args[3] == '0':
                res = delete_dir(name, args[2])
            elif args[3] == 'y':
                res = finally_delete_dir(name, args[2])
        self.sock.sendall(str.encode("\n".join(res)))
        self._close()


class Heartbeat(Thread):
    def __init__(self, sock, addr, _id):
        super().__init__(daemon=True)
        self.sock = sock
        self.sock.settimeout(heart_stop_time)
        self.addr = addr
        self.id = _id
        self.is_alive = True
        self.time_since_beat = time.time()

    def _close(self):
        # self.sock.shutdown(how=socket.SHUT_RDWR)
        if self.is_alive:
            self.is_alive = False
            del banks[self.id]
            self.sock.close()
            print('Bank %s disconnected.' % self.addr)

    def run(self):
        try:
            while self.is_alive:
                args = ['']
                try:
                    args = self.sock.recv(1024).decode('utf-8').split('\n')
                except socket.error:
                    pass
                # if time.time() - heart_stop_time > self.time_since_beat:
                message = args[0]
                if message == '1':
                    pass
                    # print("%s says hi." % self.addr)
                elif message == 'hello':
                    print("%s says hello." % self.addr)
                elif message == 'r':
                    pass
                    # todo some replica stuff
                elif self.time_since_beat + heart_stop_time < time.time():
                    self._close()
                if message != '':
                    self.time_since_beat = time.time()
            self._close()
        except:
            self._close()


class BankHandler(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, storage_port))
        self.sock.listen()

    def run(self):
        self.sock.listen()
        while True:
            con, addr = self.sock.accept()
            addr = addr[0]
            print(addr)
            banks[banks_index[0]] = Heartbeat(con, addr, banks_index[0])
            banks[banks_index[0]].start()
            banks_index[0] += 1


if __name__ == "__main__":
    host = ''
    storage_port = 19609
    guest_port = 12607
    root_filename = 'root.xml'

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, guest_port))

    banks = {}
    banks_index = [0]
    heart_stop_time = 3
    BankHandler().start()

    try:
        tree = ET.parse(root_filename)
    except IOError:
        tree = create_root()
        print("Created new root.")
    root = tree.getroot()

    sock.listen()
    while True:
        con, addr = sock.accept()
        ClientListener(con).start()
