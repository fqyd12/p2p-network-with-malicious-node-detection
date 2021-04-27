from utils import create_socket
import threading

class Peer:
  def __init__(self, pid):
    self.pid = pid

    port = 3000 + pid
    server_sock = create_socket()
    print("Creating peer on port: ",port)
    server_sock.bind(('', port))
    server_sock.listen(1)

    self.server_sock = server_sock

    self.listening_thread = threading.Thread(target=self.handle_incoming_connection)
    self.listening_thread.start()

    self.peer_socks = {}

  def handle_incoming_connection(self):
    while True:
      try:
        incoming_peer_sock, incoming_peer_addr = self.server_sock.accept()

        print(incoming_peer_addr, "connected to", self.server_sock.getsockname())
      except KeyboardInterrupt:
        break
    
    self.disconnect()

  def connect_to(self, pid):
    port = 3000 + pid
    
    sock = create_socket()
    sock.connect(('127.0.0.1', port))

    self.peer_socks[pid] = sock
  
  def disconnect(self):
    for sock in self.peer_socks:
      sock.close()

    self.listening_thread.join()

    self.server_sock.close()