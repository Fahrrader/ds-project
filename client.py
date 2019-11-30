from os import path
from time import sleep
import socket


def show_help():
    print('init         -- to initialize a new repository with this IP address.')
    print('c [filename] -- create an empty file in your directory.')
    print('r [filename] -- store and open a file from your directory.')  # TODO if read multiple times, replace local
    print('w [filename] -- send a file from your computer to the directory with replacing the old one.')
    print('d [filename] -- delete a file from your directory.')
    print('i [filename] -- display information about a file in your directory.')
    print('cp [filename] [path] -- store a copy of a file in the new path.')
    print('mv [filename] [path] -- store the file in the new path.')
    print('cd [path]    -- change the current directory.')
    print('ls           -- list the files in the current directory.')
    print('md [path]    -- make a new directory in the current directory.')
    print('d [path]     -- delete a directory from the current directory.')  # TODO support both files and dirs
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


def connect():
    sock.connect((server_ip, port))
    sock.send(str.encode(user, 'utf-8'))
    print("Connection established.")  # test


def close():
    # sock.shutdown(how=socket.SHUT_RDWR)
    sock.close()


if __name__ == "__main__":
    user = "Unknown"
    while True:
        user = input("Welcome! State your username in order to access the file sharing system: ")
        if not error_forbidden_symbols(user):
            break

    server_ip = 'localhost'  # TODO
    port = 8800
    sock = socket.socket()
    connect()  # test

    current_dir = "root"
    while True:
        command = input(current_dir + '>')
        args = command.split()
        c = args[0]
        args = args[1:]
        if c == 'help':
            show_help()
        if c == 'exit' or c == 'quit' or c == 'e' or c == 'q' or c == 'x' or c == 'close':
            close()
            print('bye-bye')
            sleep(0.1)
            break

        elif c == 'init':

            print("Initialized a new system.")
        elif c == 'c':
            if error_arg_len(expected_len=1) or error_forbidden_symbols(args[0]):
                continue

        elif c == 'r':
            if error_arg_len(expected_len=1):
                continue

        elif c == 'w':
            if error_arg_len(expected_len=1) or error_forbidden_symbols(args[0]):
                continue

        elif c == 'd':
            if error_arg_len(expected_len=1):
                continue

        elif c == 'i':
            if error_arg_len(expected_len=1):
                continue

        elif c == 'cp':
            if error_arg_len(expected_len=2) or error_forbidden_symbols(args[1]):
                continue

        elif c == 'mv':
            if error_arg_len(expected_len=2):
                continue

        elif c == 'cd':
            if error_arg_len(expected_len=1):
                continue
            # TODO set current_dir to new after all
            # current_dir = current_dir + '\\' + args[0]  # path.join(current_dir, args[0])
        elif c == 'ls':
            if error_arg_len(expected_len=1):
                continue

        elif c == 'md':
            if error_arg_len(expected_len=1) or error_forbidden_symbols(args[0]):
                continue
            # TODO put restrictions on names (\|/"*':<>) and empty

        else:
            print("Unrecognized. Try 'help' if in doubt.")

