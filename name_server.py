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
    return path[:file_begins_at] if file_begins_at != -1 else "", path[file_begins_at+1:]


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


def read_file(user, path):
    file, node = get_file(user, path)
    if node is None:
        return '0'
    if file is None:
        return '2'
    # TODO return IP, id
    return


def write_file(user, path):
    file, node = get_file(user, path)
    if node is None:
        return '0'
    if file is None:
        return '2'
    # TODO return IP, id
    # wait for ack from bank
    file.set('modified', str(datetime.datetime.now()))
    file.set('size', '0')  # change
    # send signal to bank to update all others
    return '1'


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
        # name, command = [i for i in self.sock.recv(2048).decode('utf-8').split('\n')]
        args = self.sock.recv(4096).decode('utf-8').split('\n')
        name = args[0]
        command = args[1]
        print(name + ' commands ' + command)
        self.name = name
        res = '0'

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


if __name__ == "__main__":
    host = ''
    port = 8800
    root_filename = 'root.xml'

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))

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
