import socket
import threading
import sys

MSG_SIZE = 1024
DEFAULT_PORT = 9999

clients = set()

def print_host_stats():
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        print("Hostname :  ", host_name)
        print("IP : ", host_ip)
    except:
        print("Unable to get Hostname and IP")
    

def get_host_ip():
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    return host_ip


def broadcast(message: bytes):
    for client in clients:
        client.sendall(message)


def handle_client(client_socket: socket.socket):
    while True:
        try:
            msg = client_socket.recv(MSG_SIZE)
            broadcast(msg)
        except Exception as e:
            print(f'Client disconnected: {e}')
            clients.remove(client_socket)
            client_socket.close()
            exit(0)


def connect_client(conn: socket.socket, addr: str):
    print(f"Client {addr} connected")
    clients.add(conn)
    client_thread = threading.Thread(target=handle_client, args=(conn,), daemon=True)
    client_thread.start()


def listen_for_connections(port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listen_socket:
        host_ip = get_host_ip()

        listen_socket.bind((host_ip, port))
        listen_socket.listen()

        while True:
            try:
                conn, saddr = listen_socket.accept()  
                connect_client(conn, saddr)
            except:
                print(f'{saddr} couldn\'t connect')

def run_server(port: int):
    print_host_stats()

    listen_thread = threading.Thread(target=listen_for_connections, args=(port,), daemon=True)
    listen_thread.start()


def get_port():
    if len(sys.argv) == 1:
        return DEFAULT_PORT

    if len(sys.argv) != 3 or not sys.argv[1] == '-p' or not sys.argv[2].isnumeric():
        print("Use: python server.py -p port")
        exit(0)

    return int(sys.argv[2])


def run_console():
    while True:
        command = input()

        if command == 'exit':
            broadcast("Server closed".encode())
            exit(0)

if __name__ == '__main__':
    print("Server starting...")
    run_server(get_port())
    run_console()
