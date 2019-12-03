import sys
import os
import socket
import webbrowser
from time import sleep


def show_help():
    print('init         -- to initialize a new repository with this IP address.')
    print('c [filename] -- create an empty file in your directory.')
    print('r [filename] -- store and open a file from your directory.')
    print(
        'w [filename] -- send_recv_name_server a file from your computer to the directory with replacing the old one.')
    print('d [filename] -- delete a file from your directory.')
    print('i [filename] -- display information about a file in your directory.')
    print('cp [filename] [path] -- store a copy of a file in the new path.')
    print('mv [filename] [path] -- store the file in the new path.')
    print('cd [path]    -- change the current directory.')
    print('ls           -- list the files in the current directory.')
    print('md [path]    -- make a new directory in the current directory.')
    print('dd [path]    -- delete a directory from the current directory.')
    print('help         -- list all commands.')
    print('exit         -- close the connection and the program.')
    print('quit         -- same as exit.')
    print('e            -- same as exit.')
    print('q            -- same as exit.')


def error_forbidden_symbols(name):
    forbidden_chars = ['\\', '|', '/', '"', '*', '\'', ':', '<', '>']
    error = name.strip() == '' or any(c in name for c in forbidden_chars)
    if error:
        print('The following characters cannot be used here: \\|/"*\':<>')
    return error


def error_arg_len(expected_len):
    if len(args) != expected_len:
        print("Unexpected number of arguments.")
        return True


def parse_path(current_dir, new_path):
    temp_dir = current_dir
    for d in new_path.split('\\'):
        if d == '..':
            return_index = temp_dir.rfind('\\')
            temp_dir = temp_dir[:return_index] if return_index != -1 else ""
            continue
        if error_forbidden_symbols(d):
            temp_dir = current_dir
            break
        temp_dir += ('\\' if temp_dir != "" else "") + d
    return temp_dir


def send_recv_name_server(args):
    sock = socket.socket()
    sock.settimeout(15)
    try:
        sock.connect((server_ip, port))
        sock.sendall(str.encode("\n".join(args)))
        res = sock.recv(4096).decode('utf-8').split('\n')
        if len(res) == 1:
            res = res[0]
    except socket.error:
        print("The connection has taken too long and timed out.")
        res = '0'
    except ConnectionRefusedError:
        print("The service is currently unavailable.")
        res = '0'
    sock.close()
    return res


def send_storage(file_name, file_id, storage_ip):
    sock = socket.socket()
    try:
        with open(storage_name + '/' + file_name, 'rb') as f:
            file_size = os.fstat(f.fileno()).st_size

            print(storage_ip + str(port))
            sock.connect((storage_ip, port))
            sock.sendall(str.encode("\n".join(['w', file_id, str(file_size)])))
            print('okay')

            l = f.read(chunk_size)
            while l:
                print('process')
                sock.send(l)
                l = f.read(chunk_size)
        sock.close()
        return '1'
    except IOError:  # todo
        print("Something went wrong with transmitting.")
        return '0'


def recv_storage(file_name, file_id, storage_ip):
    # for cases when we receive a file from the server
    sock = socket.socket()
    try:
        sock.connect((storage_ip, port))
        # connected storage server
        sock.sendall(str.encode("\n".join(['r', file_id])))
        file_size = int(sock.recv(1024))
        with open(storage_name + '/' + file_name, 'wb') as f:
            while True:
                data = sock.recv(chunk_size)
                if not data:
                    sock.close()
                    if file_size == os.fstat(f.fileno()).st_size:
                        return '1'
                    else:
                        return '0'
                f.write(data)
    except IOError:  # todo
        print("Something went wrong with transmitting.")
        return '0'


if __name__ == "__main__":
    user = "Unknown"
    while True:
        user = input("Welcome! State your username in order to access the file sharing system: ").strip()
        if not error_forbidden_symbols(user):
            break

    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
    else:
        server_ip = '50.19.187.186'  # TODO
    port = 12607
    sock_name_server = socket.socket()
    sock_storage = socket.socket()
    chunk_size = 1024

    storage_name = 'storage'
    try:
        os.mkdir(storage_name)
    except FileExistsError:
        pass
    current_dir = ""
    while True:
        command = input(user + ('\\' + current_dir if current_dir != "" else current_dir) + '> ')
        args = command.split()
        if len(args) == 0:
            continue
        c = args[0]
        args = args[1:]

        if c == 'help':
            show_help()

        elif c == 'exit' or c == 'quit' or c == 'e' or c == 'q' or c == 'x' or c == 'close':
            print('bye-bye')
            sleep(0.1)
            break

        elif c == 'init':
            res = send_recv_name_server([user, 'init'])
            if res == '1':
                print("Initialized a new system.")
            else:
                print("Error while initializing a new system.")

        elif c == 'c':
            if error_arg_len(expected_len=1) or error_forbidden_symbols(args[0]):
                continue
            res = send_recv_name_server([user, 'c', current_dir + '\\' + args[0]])
            if res == "1":
                print('New file %s has been successfully created.' % args[0])
            elif res == "2":
                print('File %s already exists in this directory.' % args[0])
            elif res == "0":
                print("Sorcery! It didn't work.")

        elif c == 'r':
            if error_arg_len(expected_len=1):
                continue
            res = send_recv_name_server([user, 'r', current_dir + '\\' + args[0]])
            if len(res) > 1:
                print('my gosh!')
                res = recv_storage(args[0], res[0], res[1])
            if res == '1':
                webbrowser.open(storage_name + '/' + args[0])
            elif res == '2':
                print('There is no such file in the current directory.')
            else:
                print("Sorcery! It didn't work.")

        elif c == 'w':
            if error_arg_len(expected_len=1) or error_forbidden_symbols(args[0]):
                continue
            res = send_recv_name_server([user, 'w', current_dir + '\\' + args[0]])
            if len(res) > 1:
                print('rescue mission!')
                res = send_storage(args[0], res[0], res[1])
            if res == '1':
                print("The file has been successfully writen.")
            else:
                print("Sorcery! It didn't work.")

        elif c == 'd':
            if error_arg_len(expected_len=1):
                continue
            res = send_recv_name_server([user, 'd', current_dir + '\\' + args[0]])
            if res == '1':
                print('The file has been deleted.')
            elif res == '2':
                print('There is no such file in the current directory.')
            else:
                print("Sorcery! It didn't work.")

        elif c == 'i':
            if error_arg_len(expected_len=1):
                continue
            res = send_recv_name_server([user, 'i', current_dir + '\\' + args[0]])
            if res == '2':
                print("This file doesn't exist.")
            elif res == '0':
                print("Sorcery! It didn't work.")
            else:
                print('size: %s bytes' % res[0])
                print('created: %s' % res[1])
                print('modified: %s' % res[2])

        elif c == 'cp':
            if error_arg_len(expected_len=2) or error_forbidden_symbols(args[1]):
                continue
            res = send_recv_name_server([user, 'cp', current_dir + '\\' + args[0], parse_path(current_dir, args[1])])
            if res == '1':
                continue
            elif res == '2':
                print("This file doesn't exist.")
            elif res == '3':
                print("This directory doesn't exist.")
            elif res == '4':
                print("This directory already contains a file with the same name.")
            elif res == "0":
                print("Sorcery! It didn't work.")

        elif c == 'mv':
            if error_arg_len(expected_len=2):
                continue
            res = send_recv_name_server([user, 'mv', current_dir + '\\' + args[0], parse_path(current_dir, args[1])])
            if res == '1':
                continue
            elif res == '2':
                print("This file doesn't exist.")
            elif res == '3':
                print("This directory doesn't exist.")
            elif res == '4':
                print("This directory already contains a file with the same name.")
            else:
                print("Sorcery! It didn't work.")

        elif c == 'cd':
            if error_arg_len(expected_len=1):
                continue
            temp_dir = parse_path(current_dir, args[0])
            if temp_dir == current_dir:
                continue
            res = send_recv_name_server([user, 'cd', temp_dir])
            if res == '1':
                current_dir = temp_dir  # path.join(current_dir, args[0])
            elif res == '2':
                print("This directory doesn't exist.")
            else:
                print("Sorcery! It didn't work.")

        elif c == 'ls':
            res = send_recv_name_server([user, 'ls', current_dir])
            if not res or res[0] == '0':
                print("This directory is empty.")
            elif len(res[0]) == 1:
                print(res)
            else:
                for i in res:
                    print(i)

        elif c == 'md':
            if error_arg_len(expected_len=1) or error_forbidden_symbols(args[0]):
                continue
            res = send_recv_name_server([user, 'md', current_dir + '\\' + args[0]])
            if res != '1':
                print("Sorcery! It didn't work.")

        elif c == 'dd':
            if error_arg_len(expected_len=1) or error_forbidden_symbols(args[0]):
                continue
            res = send_recv_name_server([user, 'dd', current_dir + '\\' + args[0], '0'])
            if res == '9':
                while res != 'y' and res != 'n' and res != '':
                    res = input('The directory is not empty. Do you want to proceed? (Y/n)').strip().lower()
                if res == 'y' or res == '':
                    res = send_recv_name_server([user, 'dd', current_dir + '\\' + args[0], 'y'])
            if res == '1':
                continue
            elif res == '2':
                print("This directory doesn't exist.")
            else:
                print("Sorcery! It didn't work.")

        else:
            print("Unrecognized. Try 'help' if in doubt.")
