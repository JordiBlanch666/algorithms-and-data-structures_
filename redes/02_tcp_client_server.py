"""
TCP Client / Server — how two programs talk to each other over a network.

TCP (Transmission Control Protocol) is the backbone of reliable internet
communication. It guarantees that data arrives in order and without errors.
HTTP, SSH, FTP — they all run on top of TCP.

The client-server model:
  SERVER  → binds to an address, listens for connections, waits
  CLIENT  → connects to the server, sends a message, reads the reply

This script can run in two modes:
  python 02_tcp_client_server.py server   ← start the server first
  python 02_tcp_client_server.py client   ← then connect with the client

Socket lifecycle:
  socket() → bind() → listen() → accept() → recv()/send() → close()
  (server)

  socket() → connect() → send()/recv() → close()
  (client)
"""

import socket
import sys


HOST = "127.0.0.1"   # localhost — traffic stays on this machine, never hits the network
PORT = 65432         # ports above 1024 are safe to use without admin privileges


def run_server() -> None:
    """
    Create a socket, bind it to an address, and wait for one client.
    Each message from the client is echoed back in uppercase.
    """
    # AF_INET = IPv4 address family
    # SOCK_STREAM = TCP (reliable, ordered byte stream)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        # SO_REUSEADDR lets us restart the server immediately after stopping it,
        # without waiting for the OS to release the port (usually ~60 seconds).
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server_socket.bind((HOST, PORT))
        server_socket.listen()   # start accepting connection requests

        print(f"  Server listening on {HOST}:{PORT} ...")
        print("  Waiting for a client to connect...\n")

        # accept() blocks here until a client connects.
        # It returns a NEW socket for that specific client,
        # plus the client's (ip, port) address.
        conn, addr = server_socket.accept()

        with conn:
            print(f"  Client connected from {addr}")
            while True:
                # recv() also blocks until data arrives.
                # 1024 is the buffer size in bytes — enough for short messages.
                data = conn.recv(1024)
                if not data:
                    # Empty data means the client closed the connection.
                    break

                message = data.decode("utf-8")
                print(f"  Received: '{message}'")

                # Echo back in uppercase as a simple transformation.
                response = message.upper()
                conn.sendall(response.encode("utf-8"))
                print(f"  Sent:     '{response}'")

        print("\n  Connection closed.")


def run_client() -> None:
    """
    Connect to the server and send a few messages.
    """
    messages = [
        "hello from the client",
        "networking is just two programs talking",
        "tcp guarantees delivery and order",
    ]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        print(f"  Connected to server at {HOST}:{PORT}\n")

        for msg in messages:
            client_socket.sendall(msg.encode("utf-8"))
            print(f"  Sent:     '{msg}'")

            response = client_socket.recv(1024).decode("utf-8")
            print(f"  Received: '{response}'\n")

    print("  Connection closed.")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("server", "client"):
        print("Usage:")
        print("  python 02_tcp_client_server.py server")
        print("  python 02_tcp_client_server.py client")
        sys.exit(1)

    if sys.argv[1] == "server":
        run_server()
    else:
        run_client()
