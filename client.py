import os
import webbrowser
from time import sleep
import socket


def show_help():
    print('init         -- to initialize a new repository with this IP address.')
    print('c [filename] -- create an empty file in your directory.')
    print('r [filename] -- store and open a file from your directory.')  # TODO if read multiple times, replace local
    print('w [filename] -- send_recv_name_server a file from your computer to the directory with replacing the old one.')
    print('d [filename] -- delete a file from your directory.')
    print('i [filename] -- display information about a file in your directory.')
    # TODO if we have time, make rename
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
    sock.connect((server_ip, port))
    sock.sendall(str.encode("\n".join(args)))
    try:
        res = sock.recv(4096).decode('utf-8').split('\n')
    except socket.error:
        print("The connection has taken too long and timed out.")
        return None
    if len(res) == 1:
        res = res[0]
    sock.close()
    return res


def send_storage(args, storage_ip, storage_port):
    # in cases we just send something to the storage server to store
    sock = socket.socket()
    sock.connect((storage_ip, storage_port))
    # connected storage server
    sock.sendall(str.encode("\n".join(args)))
    res = sock.recv(2048).decode('utf-8').split('\n')
    sock.close()
    # kinda ack to know if everything is ok
    return res[0]


def recv_storage(args, storage_ip, storage_port):
    # for cases when we recieve a file from the server
    sock = socket.socket()
    sock.connect((storage_ip, storage_port))
    # connected storage server
    f = open(args[1])
    data = sock.recv(1024)
    sock.close()
    if not data:
        f.close()
    else:
        f.write(data)
        f.close()
    return '1'


if __name__ == "__main__":
    user = "Unknown"
    while True:
        user = input("Welcome! State your username in order to access the file sharing system: ")
        if not error_forbidden_symbols(user):
            break

    server_ip = 'localhost'  # TODO
    port = 8800
    sock_name_server = socket.socket()
    sock_storage = socket.socket()
    # connect_name_server()  # test

    current_dir = ""
    while True:
        command = input(user + ('\\' + current_dir if current_dir != "" else current_dir) + '> ')
        args = command.split()
        c = args[0]
        args = args[1:]
        if c == 'help':
            show_help()

        if c == 'exit' or c == 'quit' or c == 'e' or c == 'q' or c == 'x' or c == 'close':
            print('bye-bye')
            sleep(0.1)
            break

        elif c == 'init':
            ack = send_recv_name_server([user, 'init'])
            if ack == '1':
                print("Initialized a new system.")
            else:
                print("Error while initializing the new system.")

        elif c == 'c':
            if error_arg_len(expected_len=1) or error_forbidden_symbols(args[0]):
                continue
            ack = send_recv_name_server([user, 'c', current_dir + '\\' + args[0]])
            if ack == "1":
                print('A new file %s has been successfully created.' % args[0])
            elif ack == "2":
                print('File %s already exists in this directory.' % args[0])
            elif ack == "0":
                print('Error while creating a new file.')

        elif c == 'r':
            if error_arg_len(expected_len=1):
                continue
            ack = send_recv_name_server([user, 'r', current_dir + '\\' + args[0]])
            storage_ip = ack[0]
            storage_port = ack[1]
            ack = recv_storage(['r', current_dir + '/%s' % args[0]])
            if ack == '1':
                webbrowser.open(args[0])
            else:
                print("Some error has occurred.")

        elif c == 'w':
            if error_arg_len(expected_len=1) or error_forbidden_symbols(args[0]):
                continue
            ack = send_recv_name_server([user, 'r', current_dir + '\\' + args[0]])
            storage_ip = ack[0]
            storage_port = ack[1]
            f = open(args[0])
            l = f.read()
            ack = send_storage(args, storage_ip, storage_port)
            if ack == '1':
                print("The file has been successfully writen.")
            else:
                print("Some error has occurred.")

        elif c == 'd':
            if error_arg_len(expected_len=1):
                continue
            ack = send_recv_name_server([user, 'd', current_dir + '\\' + args[0]])
            if ack == 1:
                print('The operation has been successfully done.')
            elif ack == 2:
                print('There is no such file or directory in the current directory.')
            else:
                print("Some error has occurred.")

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
            print(send_recv_name_server([user, 'ls', current_dir]))

        elif c == 'md':
            if error_arg_len(expected_len=1) or error_forbidden_symbols(args[0]):
                continue
            res = send_recv_name_server([user, 'md', current_dir + '\\' + args[0]])
            if res != '1':
                print("Sorcery! It didn't work.")

        elif c == 'dd':
            if error_arg_len(expected_len=1) or error_forbidden_symbols(args[0]):
                continue
            res = send_recv_name_server([user, 'dd', current_dir + '\\' + args[0]])
            if res == '1':
                continue
            elif res == '2':
                print("This directory doesn't exist.")
            else:
                print("Sorcery! It didn't work.")

        else:
            print("Unrecognized. Try 'help' if in doubt.")
