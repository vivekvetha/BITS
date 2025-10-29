import socket
import os

HOST = '172.17.0.3' # SERVER1 IP
PORT1 = 5001
SERVER2_HOST = '172.17.0.4' # SERVER2 IP
SERVER2_PORT = 5002
BUF_SIZE = 4096

def get_file_from_server2(filename):
    """
    Connects to SERVER2 and retrieves the file as bytes.
    Returns None if SERVER2 responds with NOT_FOUND.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
            s2.connect((SERVER2_HOST, SERVER2_PORT))
            s2.sendall(filename.encode())
            chunks = []
            while True:
                data = s2.recv(BUF_SIZE)
                if not data:
                    break
                chunks.append(data)
            content = b''.join(chunks)
            if content == b"NOT_FOUND":
                return None
            return content
    except Exception as e:
        print(f"SERVER1: Could not connect to SERVER2: {e}")
        return None

# Main SERVER1 loop
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT1))
    s.listen()
    print(f"SERVER1 listening on {PORT1}...")

    while True:
        conn, addr = s.accept()
        with conn:
            print(f"SERVER1: Connected by {addr}")
            filename = conn.recv(BUF_SIZE).decode().strip()
            print(f"SERVER1 received file request: {filename}")

            # Read local file
            local_content = None
            if os.path.isfile(filename):
                with open(filename, "rb") as f:
                    local_content = f.read()
                print("SERVER1: Found file locally.")

            # Get file from SERVER2
            server2_content = get_file_from_server2(filename)
            if server2_content:
                print("SERVER1: Received file from SERVER2.")
            else:
                print("SERVER1: File not found on SERVER2.")

            # Decide what to send to client
            if local_content and server2_content:
                if local_content == server2_content:
                    conn.sendall(b"SERVER1: Both servers have identical file. Sending file...\n")
                    conn.sendall(local_content)
                else:
                    conn.sendall(b"SERVER1: File differs between servers. Sending both versions...\n---SERVER1 VERSION---\n")
                    conn.sendall(local_content)
                    conn.sendall(b"\n---SERVER2 VERSION---\n")
                    conn.sendall(server2_content)
            elif local_content:
                conn.sendall(b"SERVER1: File only found locally. Sending file...\n")
                conn.sendall(local_content)
            elif server2_content:
                conn.sendall(b"SERVER1: File only found on SERVER2. Sending file...\n")
                conn.sendall(server2_content)
            else:
                conn.sendall(b"File not found on SERVER1 or SERVER2.\n")
