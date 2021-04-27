import sys
import threading
from utils import create_socket
from constants import TRACKER_PORT

class IncomingPeer:
  def __init__(self, pid):    
    sock = create_socket()
    sock.connect(('127.0.0.1', TRACKER_PORT))

    sock.close()

if __name__ == "__main__":
  pid = int(sys.argv[1])
  peer = IncomingPeer(pid)