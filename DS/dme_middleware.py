import threading
import time
import json
import socket
from datetime import datetime
from collections import deque

# --- GLOBAL CONFIGURATION ---
# The Middleware needs to know its peers and the server address
# These are placeholders; actual values are passed during initialization
SERVER_ADDR = ("SERVER_IP", 5000)
PEER_NODES = {}  # {ID: (IP, PORT)}

# --- SYNCHRONIZATION PRIMITIVES ---
# Locks for thread-safe access to shared state
LC_LOCK = threading.Lock()
STATE_LOCK = threading.Lock()

# Threading.Event is used to block the application thread until all N-1 replies are received
REPLY_EVENT = threading.Event()

# --- RICART-AGRAWALA STATE ---
# DME State Variables
LAMPORT_CLOCK = 0
NODE_ID = 0
REQUEST_TIMESTAMP = float("inf")  # Timestamp of this node's current request
REPLY_COUNT = 0
DEFERRED_REPLIES = (
    deque()
)  # Queue to store IDs of peers whose replies were deferred [3, 4]
WAITING_FOR_CS = False
IN_CRITICAL_SECTION = False
TIMEOUT_SECONDS = 15  # Timeout for waiting for replies


# --- LOGGING UTILITY ---
def log_event(event_type, details=""):
    """Logs critical events in a structured JSON format."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    with LC_LOCK:
        clock_value = LAMPORT_CLOCK

    log_entry = {
        "time_physical": timestamp,
        "node_id": NODE_ID,
        "lamport_clock": clock_value,
        "event_type": event_type,
        "details": details,
    }
    print(f"DME_LOG: {json.dumps(log_entry)}")


# --- LAMPORT CLOCK MECHANISM ---
def update_lamport_clock(received_ts=0):
    """Updates the local Lamport clock based on local event or received message."""
    with LC_LOCK:
        global LAMPORT_CLOCK
        LAMPORT_CLOCK = max(LAMPORT_CLOCK, received_ts) + 1
        return LAMPORT_CLOCK


# --- NETWORK COMMUNICATION ---
def send_message(target_ip, target_port, msg_type, data={}):
    """Utility to serialize and send a message to a peer node."""
    try:
        current_ts = update_lamport_clock()  # Increment clock before sending

        message = {"type": msg_type, "sender_id": NODE_ID, "ts": current_ts, **data}

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((target_ip, target_port))
            s.sendall(json.dumps(message).encode("utf-8"))

        if msg_type == "DME_REQUEST":
            log_event(
                "REQUEST_SENT", f"T={current_ts}, Target=({target_ip}:{target_port})"
            )
        elif msg_type == "DME_REPLY":
            log_event(
                "REPLY_SENT", f"T={current_ts}, Target=({target_ip}:{target_port})"
            )

    except Exception as e:
        log_event(
            "NETWORK_ERROR",
            f"Failed to send {msg_type} to {target_ip}:{target_port}: {e}",
        )


# --- RICART-AGRAWALA PROTOCOL ROUTINES ---


def acquire_write_lock():
    """Application calls this to request entry to the Critical Section (CS). Blocks until granted."""
    global REQUEST_TIMESTAMP, WAITING_FOR_CS, REPLY_COUNT

    with STATE_LOCK:
        REPLY_COUNT = 0
        REPLY_EVENT.clear()
        WAITING_FOR_CS = True

        # 1. Update clock and record request timestamp
        REQUEST_TIMESTAMP = update_lamport_clock()
        current_ts = REQUEST_TIMESTAMP

    log_event("CS_REQUESTED", f"Starting request, T={current_ts}")

    # 2. Broadcast REQUEST to all other nodes
    for peer_id, (ip, port) in PEER_NODES.items():
        send_message(ip, port, "DME_REQUEST", {"req_ts": current_ts, "req_id": NODE_ID})

    # 3. Wait for N-1 replies (N-1 = 1 in this 2-node DME system)
    if REPLY_EVENT.wait(timeout=TIMEOUT_SECONDS):
        with STATE_LOCK:
            global IN_CRITICAL_SECTION
            IN_CRITICAL_SECTION = True
        log_event(
            "CS_ENTERED",
            f"Lock acquired after receiving all replies (Reply Count={REPLY_COUNT})",
        )
        return True
    else:
        # Timeout occurred - clean up state
        with STATE_LOCK:
            WAITING_FOR_CS = False
            REQUEST_TIMESTAMP = float("inf")
        log_event("CS_TIMEOUT", "Failed to acquire lock within timeout period.")
        return False


def release_write_lock():
    """Application calls this to exit the Critical Section."""
    global IN_CRITICAL_SECTION, REQUEST_TIMESTAMP

    with STATE_LOCK:
        # 1. Exit CS state
        IN_CRITICAL_SECTION = False
        REQUEST_TIMESTAMP = float("inf")

        log_event("CS_EXITED", "Critical Section execution finished. Releasing lock.")

        # 2. Send deferred replies [3, 4]
        while DEFERRED_REPLIES:
            peer_id = DEFERRED_REPLIES.popleft()
            if peer_id in PEER_NODES:
                ip, port = PEER_NODES[peer_id]
                send_message(ip, port, "DME_REPLY")
                log_event("DEFERRED_REPLY_SENT", f"Sent reply to Node {peer_id}")


def handle_dme_reply(msg):
    """Processes an incoming REPLY message."""
    global REPLY_COUNT

    ts = msg.get("ts", 0)
    update_lamport_clock(ts)

    with STATE_LOCK:
        if WAITING_FOR_CS:
            REPLY_COUNT += 1
            log_event(
                "REPLY_RCVD",
                f"Received reply from Node {msg['sender_id']}. Count: {REPLY_COUNT}",
            )

            # If all replies are received (N-1 = 1)
            if REPLY_COUNT == len(PEER_NODES):
                REPLY_EVENT.set()


def handle_dme_request(msg):
    """Processes an incoming REQUEST message, applying deferral logic."""
    global DEFERRED_REPLIES

    req_ts = msg.get("req_ts", 0)
    req_id = msg.get("req_id", 0)

    # 1. Clock Synchronization
    update_lamport_clock(req_ts)

    with STATE_LOCK:
        # Determine if the incoming request has higher priority (Pj < Pi)
        # Pj is higher priority if: (Tj < Ti) OR (Tj = Ti AND j < i)

        defer_reply = False

        # Condition 1: Local node is currently executing the CS [4]
        if IN_CRITICAL_SECTION:
            defer_reply = True

        # Condition 2: Local node is requesting and has higher priority [4]
        elif WAITING_FOR_CS:
            # Check if current node (Pi) is preferred (older request/wins tie)
            pi_preferred = (REQUEST_TIMESTAMP < req_ts) or (
                REQUEST_TIMESTAMP == req_ts and NODE_ID < req_id
            )

            if pi_preferred:
                defer_reply = True

        # Log the decision
        if defer_reply:
            DEFERRED_REPLIES.append(req_id)
            log_event(
                "REQUEST_RCVD",
                f"From Node {req_id} (T={req_ts}). Deferred REPLY. State: { 'CS' if IN_CRITICAL_SECTION else 'REQUESTING'}",
            )
        else:
            # Send immediate REPLY (Node is NCS, or Node is REQUESTING but lower priority)
            ip, port = PEER_NODES[req_id]
            send_message(ip, port, "DME_REPLY")
            log_event(
                "REQUEST_RCVD",
                f"From Node {req_id} (T={req_ts}). Immediate REPLY sent. State: NCS",
            )


def start_dme_listener(listen_port):
    """
    Sets up a thread to listen for incoming DME messages (P2P communication).
    This runs continuously in the background.[5]
    """
    listener_thread = threading.Thread(
        target=_dme_listener_loop, args=(listen_port,), daemon=True
    )
    listener_thread.start()
    return listener_thread


def _dme_listener_loop(port):
    """The main loop for the DME listener thread."""
    try:
        # Listen on 0.0.0.0 to accept connections from Docker network peers
        listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener_socket.bind(("", port))
        listener_socket.listen(5)
        log_event("DME_LISTENER_START", f"DME Listener running on Port {port}")

        while True:
            conn, addr = listener_socket.accept()
            # Handle incoming message in a new thread to avoid blocking the listener [6]
            threading.Thread(
                target=_handle_incoming_connection, args=(conn, addr), daemon=True
            ).start()

    except Exception as e:
        log_event("DME_LISTENER_ERROR", f"Listener failed: {e}")


def _handle_incoming_connection(conn, addr):
    """Handles an individual incoming DME message."""
    try:
        data = conn.recv(4096)
        if data:
            message = json.loads(data.decode("utf-8"))
            msg_type = message.get("type")

            if msg_type == "DME_REQUEST":
                handle_dme_request(message)
            elif msg_type == "DME_REPLY":
                handle_dme_reply(message)

    except Exception as e:
        log_event("MESSAGE_HANDLER_ERROR", f"Error processing message from {addr}: {e}")
    finally:
        conn.close()
