import threading
import socket
import queue

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 7777

packets_q = queue.Queue()
clients = []

def client_handle(client):
  try:
    clients.append(client)
    while True:
      full_data = b""
      error = False
      while True:
        chunk = client.recv(2048)
        if len(chunk) <= 0:
          error = True
          break
        full_data += chunk
        if full_data.endswith(b"</data>"): break
      if error: break
      packets_q.put(full_data)
  except Exception:
    return
  finally:
    clients.remove(client)

def broadcast():
  while True:
    packet = packets_q.get()
    current_clients = clients.copy()
    for client in current_clients:
      try:
        client.send(packet)
      except Exception as e:
        print(e)
        continue

def main():
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind((SERVER_HOST, SERVER_PORT))
  sock.listen()
  print(f"Listening to {SERVER_HOST}:{SERVER_PORT}...")
  threading.Thread(target=broadcast, daemon=True).start()

  while True:
    try:
      client, client_address = sock.accept()
      threading.Thread(target=client_handle, args=[client], daemon=True).start()
    except KeyboardInterrupt:
      return

if __name__ == "__main__":
  main()
