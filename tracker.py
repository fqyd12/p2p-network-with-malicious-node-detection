import sys
import threading
from utils import create_socket
from peer import Peer
from constants import TRACKER_PORT

class Tracker:
  def __init__(self):
    self.peer_list = []

    tracker_sock = create_socket()
    tracker_sock.bind(('', TRACKER_PORT))

    print("Tracker port:", TRACKER_PORT)

    tracker_sock.listen(1)

    self.tracker_sock = tracker_sock

    self.listening_thread = threading.Thread(target=self.start_tracking)
    self.listening_thread.start()

  def start_tracking(self):
    while True:
      try:
        peer_sock, peer_addr = self.tracker_sock.accept()

        print("New incoming peer:", peer_addr)

        new_peer_id = len(self.peer_list)+1
        new_peer = Peer(new_peer_id)

        for peer in self.peer_list:
          new_peer.connect_to(peer.pid)
          peer.connect_to(new_peer_id)

        self.peer_list.append(new_peer)
      except KeyboardInterrupt:
        break
    
    for peer in self.peer_list:
      peer.disconnect()
    
    self.listening_thread.join()
    self.tracker_sock.close()

if __name__ == "__main__":
  tracker = Tracker()