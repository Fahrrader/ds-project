import socket
import string
import xml.etree.ElementTree as ET
from threading import Thread
from random import choices, shuffle
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


def get_last_node_split(path: str):
    file_begins_at = path.rfind('\\')
    return path[:file_begins_at] if file_begins_at != -1 else "", path[file_begins_at + 1:]


def get_file(user, path: str):
    cut_path, file = get_last_node_split(path)
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
    for d in deleted.findall('.//f'):
        delete_file(None, None, d, node)
    node.remove(deleted)
    tree.write(root_filename)
    return '1'


def move_file(user, path, path2):
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
    file, node1 = get_file(user, path)
    if node1 is None:
        return '0'
    if file is None:
        return '2'
    old_id = file.get('id')

    _, file_path = get_last_node_split(path)
    file2, node2 = get_file(user, path2 + "\\" + file_path)
    if node2 is None:
        return '3'
    if file2 is not None:
        return '4'

    elements = ['']
    while elements:
        new_id = ''.join(choices(string.ascii_letters + string.digits, k=64))
        elements = root.findall('.//*[@id="%s"]' % new_id)

    file = ET.SubElement(node2, 'f', attrib={
        'id': new_id,
        'name': file_path,
        'size': '0',
        'created': str(datetime.datetime.now()),
        'modified': str(datetime.datetime.now())
    })

    bank = banks[choices(list(banks.keys()))[0]].addr
    sock = socket.socket()
    sock.settimeout(heart_stop_time * 2)
    try:
        sock.connect((bank, guest_port))
        sock.sendall(str.encode("\n".join(['r', new_id, old_id, bank])))
        sock.close()
    except ConnectionRefusedError:
        print("The service is currently unavailable.")
        sock.close()
        return '0'
    except socket.error:
        print("The connection took too long and timed out.")
        sock.close()
        return '0'
    return '1'


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


def get_bank_in_possession(file, k=1):
    bank_indices = get_bank_indices(file)
    bank_indices = list(map(int, bank_indices))
    if not bank_indices:
        return []
    if k != 1:
        return bank_indices

    bank = choices(bank_indices)[0]
    while not (bank in banks):
        print('lots of banks? ' + str(bank))
        bank = choices(bank_indices)[0]

    return bank


def get_bank_indices(file):
    bank_indices = file.findall('./')
    bank_indices = bank_indices if bank_indices is not None else []
    bank_indices = [bank.text for bank in bank_indices]
    print(bank_indices)  # todo
    return bank_indices
    # file.text.strip().split(',') if file.text is not None else []


def get_banks_for_possession(banks_already):
    banks_r = list(banks.keys())
    shuffle(banks_r)
    banks_r = [bank for bank in banks_r if bank not in banks_already]
    banks_r = banks_r[:min(replica_number(), banks_r.__len__())]
    banks_r = [banks[bank].addr for bank in banks_r]
    return banks_r


def replica_number():
    return min(max(int(len(banks) / 3), 3), len(banks)) - 1


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

    bank = banks[choices(list(banks.keys()))[0]].addr
    sock = socket.socket()
    sock.settimeout(heart_stop_time * 2)
    try:
        sock.connect((bank, guest_port))
        sock.sendall(str.encode("\n".join(['c', new_id])))
        sock.close()
    except ConnectionRefusedError:
        print("The service is currently unavailable.")
        sock.close()
        return '0'
    except socket.error:
        print("The connection took too long and timed out.")
        sock.close()
        return '0'

    cut_path, file_name = get_last_node_split(path)
    file = ET.SubElement(node, 'f', attrib={
        'id': new_id,
        'name': file_name,
        'size': '0',  # something
        'created': str(datetime.datetime.now()),
        'modified': str(datetime.datetime.now())
    })

    print('created file.')
    tree.write(root_filename)
    return '1'


def write_file(user, path):
    file, node = get_file(user, path)
    if node is None:
        return '0'
    if file is None:
        elements = ['']
        while elements:
            file_id = ''.join(choices(string.ascii_letters + string.digits, k=64))
            elements = root.findall('.//*[@id="%s"]' % file_id)
    else:
        file_id = file.get('id')

    if file is None:
        _, file_name = get_last_node_split(path)
        file = ET.SubElement(node, 'f', attrib={
            'id': file_id,
            'name': file_name,
            'size': '0',
            'created': str(datetime.datetime.now()),
            'modified': str(datetime.datetime.now())
        })

    print('written file.')
    tree.write(root_filename)
    banks_p = get_bank_in_possession(file, k=-1)
    return [file_id, choices(get_banks_for_possession(banks_p))[0]]


def read_file(user, path):
    file, node = get_file(user, path)
    if node is None:
        return '0'
    if file is None:
        return '2'

    file_id = file.get('id')
    bank = get_bank_in_possession(file)
    is_bank_okay = bank or bank == 0
    if not is_bank_okay and datetime.datetime.strptime(file.get('modified'), '%Y-%m-%d %H:%M:%S.%f') + datetime.timedelta(hours=heart_stop_time) < datetime.datetime.now():
        print('No one has this file. Delete.')
        delete_file(user, path)
        return '2'

    return [file_id, banks[bank].addr]


def delete_file(user, path, file=None, node=None):
    if file is None or node is None:
        file, node = get_file(user, path)
        if node is None:
            return '0'
        if file is None:
            return '2'

    bank_indices = get_bank_in_possession(file, -1)
    for bank in bank_indices:
        sock = socket.socket()
        sock.settimeout(heart_stop_time * 2)
        try:
            sock.connect((banks[bank].addr, guest_port))
            sock.send(str.encode("\n".join(['d', file.get('id')])))
            sock.close()
        except ConnectionRefusedError:
            print("The service is currently unavailable.")
            sock.close()
            return '0'
        except socket.error:
            print("The connection timed out.")
            sock.close()
            return '0'

    node.remove(file)
    print('deleted file.')
    tree.write(root_filename)
    return '1'


def get_file_info(user, path):
    file, node = get_file(user, path)
    if node is None:
        return '0'
    if file is None:
        return '2'
    return [file.attrib['size'], file.attrib['created'], file.attrib['modified'], str(get_bank_indices(file))]


class ClientListener(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = ""

    def _close(self):
        self.sock.close()
        print(self.name + ' disconnected.')

    def run(self):
        args = self.sock.recv(4096).decode('utf-8').split('\n')
        name = args[0]
        command = args[1]
        print(name + ' commands ' + command)
        self.name = name
        res = '0'

        if not banks.keys():
            res = '0'
        elif command == 'init':
            res = init(name)
        elif command == 'c':
            res = create_file(name, args[2])
        elif command == 'r':
            res = read_file(name, args[2])
        elif command == 'w':
            res = write_file(name, args[2])
        elif command == 'd':
            res = delete_file(name, args[2])
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


def set_replica(file_id, file_size=None, bank_ip=None, bank_id=None):
    file = root.find('.//*[@id="%s"]' % file_id)
    if file is None:
        return

    if file_size is None:
        bank_id = choices(get_bank_indices(file))[0]
        bank_ip = banks[bank_id].addr
    else:
        # file.text = (file.text if file.text is not None else '') + (',' if file.text is not None else '') + str(bank_id)  # todo
        i = ET.SubElement(file, 'i')
        i.text = str(file_id)
        file.set('modified', str(datetime.datetime.now()))
        file.set('size', file_size)
        file.set('op', '0')
        tree.write(root_filename)

    bank_indices = get_bank_indices(file)
    if len(bank_indices) < 2:
        bank_ips = get_banks_for_possession(bank_indices)
        if bank_ips:
            print("Decided to replicate to " + str(bank_ips))
            sock = socket.socket()
            sock.settimeout(heart_stop_time * 2)
            try:
                sock.connect((bank_ip, guest_port))
                sock.sendall(str.encode("\n".join(['r', file_id, ''] + bank_ips)))
            except ConnectionRefusedError:
                print("The service is currently unavailable.")
            except socket.error:
                print("The connection timed out.")
            sock.close()


def delete_old_replicas(bank_id):
    elements = root.findall('.//*/f[i="%s"]' % bank_id)
    print(elements)


class Heartbeat(Thread):
    def __init__(self, sock, addr, _id):
        super().__init__(daemon=True)
        self.sock = sock
        self.sock.settimeout(heart_stop_time)
        self.addr = addr
        self.id = _id
        self._is_alive = True
        self.time_since_beat = time.time()

    def _close(self):
        # self.sock.shutdown(how=socket.SHUT_RDWR)
        if self._is_alive:
            self._is_alive = False
            delete_old_replicas(self.id)
            # TODO find all where text contains id -- and it is surrounded with , or is first or second element
            # go through them, strip, launch other replicas if necessary
            del banks[self.id]
            self.sock.close()
            print('Bank %s disconnected.' % self.addr)

    def run(self):
        while self._is_alive:
            args = ['']
            try:
                args = self.sock.recv(1024).decode('utf-8').split('\n')
            except socket.error:
                pass
            message = args[0]
            if message == '1':
                pass
            elif message == 'hello':
                print("%s says hello." % self.addr)
            elif message == 'r':
                print('got notified with %s' % args[1])
                set_replica(args[1], args[2], self.addr, self.id)
            elif self.time_since_beat + heart_stop_time < time.time():
                self._close()
            if message != '':
                self.time_since_beat = time.time()
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
            banks[banks_index[0]] = Heartbeat(con, addr, banks_index[0])
            banks[banks_index[0]].start()
            banks_index[0] += 1


if __name__ == "__main__":
    host = socket.gethostname()
    storage_port = 19609
    guest_port = 12607
    root_filename = 'root.xml'

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, guest_port))

    banks = {}
    banks_index = [0]
    heart_stop_time = 3
    BankHandler().start()

    # try:
        # tree = ET.parse(root_filename)
    # except IOError:
    tree = create_root()  # always create root
    print("Created new root.")
    root = tree.getroot()

    sock.listen()
    while True:
        con, addr = sock.accept()
        ClientListener(con).start()
