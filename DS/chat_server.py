import socket
import threading
import time
import json
from datetime import datetime

# --- CONFIGURATION ---
SERVER_IP = "0.0.0.0"  # Listen on all interfaces
SERVER_PORT = 5000
CHAT_FILE = "CHAT_LOG.txt"

# Local Synchronization: Lock to protect the file I/O operations from concurrent threads
# within the server process [8, 9]
FILE_LOCK = threading.Lock()

# --- SERVER API HANDLERS ---


def handle_view():
    """Handles the 'view' command (read operation). Does NOT require the local lock."""
    try:
        with open(CHAT_FILE, "r") as f:
            content = f.read()
        return "SUCCESS", content
    except FileNotFoundError:
        return "SUCCESS", "--- Chat Log Empty ---\n"
    except Exception as e:
        return "ERROR", f"Server read error: {e}"


def handle_post(message_line):
    """Handles the 'post' command (write/append operation). Requires the local lock."""
    # This operation is the Server's endpoint for the Distributed Critical Section.
    # We must ensure local thread safety.
    with FILE_LOCK:
        try:
            with open(CHAT_FILE, "a") as f:
                f.write(message_line + "\n")
            return "SUCCESS", "Message posted successfully."
        except Exception as e:
            return "ERROR", f"Server write error: {e}"


# --- CLIENT CONNECTION HANDLER ---


def client_handler(conn, addr):
    """Handles commands from a single client connection (P1 or P2)."""
    try:
        data = conn.recv(4096).decode("utf-8")
        if not data:
            return

        request = json.loads(data)
        command = request.get("command")

        print(f"Server: Received command '{command}' from {addr}")

        if command == "VIEW":
            status, response = handle_view()
        elif command == "POST":
            # The message_line already contains the required Node ID and timestamp from the client
            status, response = handle_post(request.get("message"))
        else:
            status, response = "ERROR", "Invalid command."

        # Send response back to the client node
        response_data = json.dumps({"status": status, "response": response}).encode(
            "utf-8"
        )
        conn.sendall(response_data)

    except Exception as e:
        print(f"Server error handling connection from {addr}: {e}")
    finally:
        conn.close()


# --- MAIN SERVER LOOP ---
def start_server():
    """Initializes and runs the multi-threaded chat server."""
    # Ensure the chat file exists
    if not os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "w") as f:
            f.write("--- Welcome to the Chat Room ---\n")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen(5)
        print(f"Chat Server (S) listening on {SERVER_IP}:{SERVER_PORT}...")

        while True:
            conn, addr = server_socket.accept()
            # Delegate each client request to a new thread for concurrent handling [6]
            threading.Thread(target=client_handler, args=(conn, addr)).start()

    except Exception as e:
        print(f"Server crash: {e}")
    finally:
        server_socket.close()


if __name__ == "__main__":
    import os

    start_server()
