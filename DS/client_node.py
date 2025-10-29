import socket
import json
import time
import sys
from datetime import datetime
import dme_middleware as dme  # Import the middleware module

# --- CONFIGURATION (MUST BE CHANGED PER NODE) ---
NODE_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1  # 1 for P1, 2 for P2
LISTEN_PORT = 5000 + NODE_ID  # 5001 for P1, 5002 for P2
SERVER_IP = "172.17.0.2"  #  the Actual Server (S) IP
SERVER_PORT = 5000
PEER_IP_1 = "172.17.0.3"  # P1's IP
PEER_IP_2 = "172.17.0.4"  # P2's IP

# Map of all nodes participating in DME consensus (P1 and P2)
PEER_NODES = {
    1: (PEER_IP_1, 5001),
    2: (PEER_IP_2, 5002),
}


# --- APPLICATION CLIENT UTILITY ---
def send_server_request(command, data={}):
    """Handles communication with the central Chat Server (S)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_IP, SERVER_PORT))
            request = json.dumps({"command": command, **data})
            s.sendall(request.encode("utf-8"))

            # Receive response
            response_data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response_data += chunk

            return json.loads(response_data.decode("utf-8"))

    except Exception as e:
        return {
            "status": "NETWORK_ERROR",
            "response": f"Connection to Server failed: {e}",
        }


# --- APPLICATION COMMAND LOGIC ---


def view_command():
    """
    Implements the 'view' command. This is a non-critical read operation
    and bypasses the DME middleware.
    """
    dme.log_event("VIEW_COMMAND", "Initiating non-critical read operation.")
    response = send_server_request("VIEW")

    if response["status"] == "SUCCESS":
        print("\n--- Current Chat Log ---\n" + response["response"])
    else:
        print(f"Error viewing log: {response['response']}")


def post_command(text):
    """
    Implements the 'post' command. This is the Critical Section, requiring the DME lock.
    """
    # 1. Acquire Distributed Write Lock (Entry Protocol)
    if not dme.acquire_write_lock():
        print(f"\n Node {NODE_ID} could not acquire write lock.")
        return

    try:
        # ** CRITICAL SECTION **
        # The Application logic executes the resource modification here.

        # 2. Format the message line, including local time and ID
        local_time = datetime.now().strftime("%d %b %H:%M:%S")
        message_line = f"{local_time} Node {NODE_ID}: {text}"

        # --- ARTIFICIAL DELAY SETUP ---
        # Trigger a 4-second delay only if the text input is 'DELAY_CS'
        if text == "DELAY_CS":
            dme.log_event("ARTIFICIAL_DELAY_START", "Holder delaying CS for 4 seconds")
            time.sleep(4)
        # -----------------------------

        # 3. Execute the Server RPC (Append message to shared file)
        response = send_server_request("POST", {"message": message_line})

        if response["status"] == "SUCCESS":
            print(f"\n Message: '{text}'")
        else:
            print(f"\n Server reported: {response['response']}")

    finally:
        # 4. Release Distributed Write Lock (Exit Protocol)
        dme.release_write_lock()


# --- MAIN CLI LOOP ---


def start_client_application():
    """Initializes the node, sets up the middleware, and starts the CLI."""

    # Initialize Middleware with Node-specific details
    dme.NODE_ID = NODE_ID
    dme.PEER_NODES = {k: v for k, v in PEER_NODES.items() if k != NODE_ID}

    print(f"--- Distributed Node P{NODE_ID} Initialized ---")
    print(f"DME Peers: {list(dme.PEER_NODES.keys())}, Listening on Port: {LISTEN_PORT}")

    # Start the background listener for incoming DME messages
    dme.start_dme_listener(LISTEN_PORT)

    print("Type 'view' or 'post <text>'. Type 'exit' to quit.")

    while True:
        try:
            user_input = input(f"P{NODE_ID}> ").strip()
            if not user_input:
                continue

            parts = user_input.split(" ", 1)
            command = parts[0].lower()

            if command == "exit":
                sys.exit(0)
            elif command == "view":
                view_command()
            elif command == "post":
                if len(parts) > 1:
                    post_command(parts[1].strip())
                else:
                    print("Usage: post <text>")
            else:
                print(f"Unknown command: {command}")

        except KeyboardInterrupt:
            print("\nExiting application.")
            sys.exit(0)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # Wait briefly to ensure the server and the other peer are initialized
    time.sleep(1)
    start_client_application()
