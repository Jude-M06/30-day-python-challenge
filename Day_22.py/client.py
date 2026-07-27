import socket
import threading
import sys

HOST   = "127.0.0.1"
PORT   = 5555
BUFFER = 4096

def receive_messages(client):
    while True:
        try:
            data = client.recv(BUFFER)
            if not data:
                print("\n[Disconnected from server]")
                break
            print(data.decode("utf-8"))
        except OSError:
            break

def start_client():
    nick = input("Enter your nickname: ").strip()
    if not nick:
        nick = "Anonymous"

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(f"Could not connect to {HOST}:{PORT} — is the server running?")
        sys.exit(1)

    
    client.sendall(nick.encode("utf-8"))
    print(f"Connected as '{nick}'. Type /quit to leave.\n")

    
    recv_thread = threading.Thread(
        target=receive_messages, args=(client,), daemon=True
    )
    recv_thread.start()

    
    try:
        while True:
            message = input()
            if not message:
                continue
            client.sendall(message.encode("utf-8"))
            if message.strip().lower() == "/quit":
                break
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        client.close()
        print("Disconnected.")

if __name__ == "__main__":
    start_client()