import socket
import os

HOST = '172.17.0.4' # SERVER2 IP
PORT = 5002
BUF_SIZE = 4096

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"SERVER2 listening on {PORT}...")

    while True:
        conn, addr = s.accept()
        with conn:
            print(f"SERVER2: Connected by {addr}")
            filename = conn.recv(BUF_SIZE).decode().strip()
            print(f"SERVER2 received file request: {filename}")

            if not os.path.isfile(filename):
                conn.sendall(b"NOT_FOUND")
                print("SERVER2: File not found.")
            else:
                print("SERVER2: Sending file contents...")
                with open(filename, "rb") as f:
                    while True:
                        data = f.read(BUF_SIZE)
                        if not data:
                            break
                        conn.sendall(data)
                print("SERVER2: File sent successfully.")
