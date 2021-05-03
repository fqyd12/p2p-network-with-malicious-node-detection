import sys
from utils import create_socket
from constants import TRACKER_PORT
import threading

class Peer:
  def __init__(self, port):
    self.port = port

    sock = create_socket()
    sock.connect(('127.0.0.1', TRACKER_PORT))

    num_peer_ports = int(sock.recv(5).decode("utf-8"))

    self.peer_socks = {}
    self.recv_threads = []

    if num_peer_ports > 1:
      peer_ports_str = sock.recv(num_peer_ports).decode('utf-8')
      peer_ports = peer_ports_str.split(",")
      print("Received peer list", peer_ports)

      for peer_port in peer_ports:
        if peer_port:
          self.connect_to(int(peer_port))

    server_sock = create_socket()
    print("Creating peer on port: ",port)
    server_sock.bind(('', port))
    server_sock.listen(1)

    self.server_sock = server_sock

    sock.send(str(port).encode("utf-8"))

    self.listening_thread = threading.Thread(target=self.handle_incoming_connection)
    self.listening_thread.start()

    self.listening_thread.join()

  def handle_incoming_connection(self):
    while True:
      try:
        incoming_peer_sock, incoming_peer_addr = self.server_sock.accept()

        print(incoming_peer_addr, "connected to", self.server_sock.getsockname())

        self.peer_socks[incoming_peer_addr[1]] = incoming_peer_sock
      except KeyboardInterrupt:
        break
    
    self.disconnect()

  def recv_msgs(self, sock):
    while True:
      try:
        msg = sock.recv(10)
        print(msg.decode('utf-8'))
      except KeyboardInterrupt:
        break

    sock.close()

  def connect_to(self, port):
    sock = create_socket()
    sock.connect(('127.0.0.1', port))

    self.peer_socks[port] = sock

    thread = threading.Thread(target=self.recv_msgs, args=[sock])
    thread.start()

    self.recv_threads.append(thread)
  
  def disconnect(self):
    for sock in self.peer_socks:
      sock.close()

    for thread in self.recv_threads:
      thread.join()

    self.listening_thread.join()

    self.server_sock.close()
  
  def send(self, port, msg):
    sock = self.peer_socks[port]
    sock.send(msg.encode('utf-8'))

if __name__ == "__main__":
  port = int(sys.argv[1])
  peer = Peer(port)
  print("Hi Peer",port)
  print("1. Show connected peers")
  choice = int(input())
  if choice == 1:
    for sock in peer.peer_socks:
      print(peer_sock.gethostname(), peer_sock.getpeername())