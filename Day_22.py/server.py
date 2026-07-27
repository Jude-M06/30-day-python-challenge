import socket
import threading
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5555
BUFFER = 4096

clients: dict  = {}      
lock = threading.Lock()

def timestamp():
    return datetime.now().strftime("%H:%M")

def broadcast(message: str, sender=None):
    data = message.encode("utf-8")
    with lock:
        dead = []
        for conn in clients:
            if conn is sender:
                continue
            try:
                conn.sendall(data)
            except OSError:
                dead.append(conn)
        for conn in dead:
            remove_client(conn)

def remove_client(conn):
    nick = clients.pop(conn, "unknown")
    try:
        conn.close()
    except OSError:
        pass
    return nick

def handle_client(conn, addr):
    
    try:
        nick = conn.recv(BUFFER).decode("utf-8").strip()
        if not nick:
            nick = str(addr)
    except OSError:
        conn.close()
        return

    with lock:
        clients[conn] = nick

    print(f"[{timestamp()}] {nick} connected from {addr}")
    broadcast(f"[{timestamp()}] ** {nick} joined the chat **", sender=conn)

    try:
        while True:
            data = conn.recv(BUFFER)
            if not data:
                break                        
            message = data.decode("utf-8").strip()
            if message.lower() == "/quit":
                break
            if message:
                formatted = f"[{timestamp()}] {nick}: {message}"
                print(formatted)
                broadcast(formatted, sender=conn)
    except OSError:
        pass
    finally:
        with lock:
            nick = remove_client(conn)
        broadcast(f"[{timestamp()}] ** {nick} left the chat **")
        print(f"[{timestamp()}] {nick} disconnected.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVER] Listening on {HOST}:{PORT} — Ctrl+C to stop\n")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(
                target=handle_client, args=(conn, addr), daemon=True
            )
            thread.start()
            print(f"[SERVER] Active connections: {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down.")
    finally:
        with lock:
            for conn in list(clients):
                conn.close()
        server.close()

if __name__ == "__main__":
    start_server()
