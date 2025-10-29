import socket

SERVER1 = '172.17.0.3' # SERVER1 IP
PORT = 5001
BUF_SIZE = 4096

filename = input("Enter filename: ").strip()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((SERVER1, PORT))
    s.sendall(filename.encode())

    print("Response from SERVER1:")
    while True:
        data = s.recv(BUF_SIZE)
        if not data:
            break
        print(data.decode(errors='replace'), end='')
