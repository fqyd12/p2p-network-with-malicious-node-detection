import sys
import threading
from utils import create_socket
from peer import Peer
from constants import TRACKER_PORT
import time

class Tracker:
  def __init__(self):
    self.peer_list = []

    tracker_sock = create_socket()
    tracker_sock.bind(('', TRACKER_PORT))

    print("Tracker port:", TRACKER_PORT)

    tracker_sock.listen(1)

    self.peer_socks = {}

    self.tracker_sock = tracker_sock

    self.listening_thread = threading.Thread(target=self.start_tracking)
    self.listening_thread.start()

  def start_tracking(self):
    while True:
      try:
        peer_sock, peer_addr = self.tracker_sock.accept()

        self.peer_socks[peer_addr[1]] = peer_sock

        print("New incoming peer:", peer_addr)

        peer_ports_str = ""

        for peer_port in self.peer_list:
          peer_ports_str += str(peer_port).zfill(5) + ","
        
        len_peer_ports_str = str(len(peer_ports_str)).zfill(5)

        peer_ports_str = len_peer_ports_str + peer_ports_str
        
        peer_sock.send(peer_ports_str.encode("utf-8"))

        new_port = peer_sock.recv(6).decode("utf-8")

        print(new_port)

        self.peer_list.append(int(new_port))
      except KeyboardInterrupt:
        break
    
    self.listening_thread.join()
    self.tracker_sock.close()

if __name__ == "__main__":
  tracker = Tracker()