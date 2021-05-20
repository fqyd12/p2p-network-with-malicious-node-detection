import sys
import threading
from utils import create_socket
from peer import Peer
from constants import TRACKER_PORT, REPORTS_SOCK_PORT
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import networkx as nx
import numpy as np

reports = {}

class Tracker:
  def __init__(self):
    self.peer_list = []

    tracker_sock = create_socket()
    tracker_sock.bind(('', TRACKER_PORT))

    print("Tracker port:", TRACKER_PORT)
    tracker_sock.listen(1)

    reports_sock = create_socket()
    reports_sock.bind(('', REPORTS_SOCK_PORT))

    print("Reports port:", REPORTS_SOCK_PORT)
    reports_sock.listen(1)

    self.peer_socks = {}

    self.tracker_sock = tracker_sock
    self.reports_sock = reports_sock

    self.tracking_thread = threading.Thread(target=self.start_tracking)
    self.tracking_thread.start()

    self.reports_thread = threading.Thread(target=self.listen_reports)
    self.reports_thread.start()

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

        self.peer_list.append(int(new_port))
      except KeyboardInterrupt:
        break
    
    self.tracker_sock.close()
    self.reports_sock.close()

  def get_reports(self, peer):
    if peer in reports:
      return reports[peer]
    
    return 0
  
  def listen_reports(self):
    global reports
    while True:
      try:
        peer_sock, peer_addr = self.reports_sock.accept()
        reported_port = int(peer_sock.recv(5).decode('utf-8'))
        if reported_port in reports:
          reports[reported_port] += 1
        else:
          reports[reported_port] = 1
        
        if reports[reported_port] >= 2:
          self.peer_list.remove(reported_port)

          sock = create_socket()
          sock.connect(('127.0.0.1', reported_port))

          sock.send('quitt'.encode('utf-8'))

          print("Removed", reported_port, "from the network due to malicious detection.")
        
        peer_sock.close()
      except KeyboardInterrupt:
        break


if __name__ == "__main__":
  tracker = Tracker()
  plt.ion()
  l = len(tracker.peer_list)
  s = sum(reports.values())
  while True:
    G = nx.Graph()
    labels = {}
    for peer in tracker.peer_list:
      labels[peer] = str(peer) + "\nr: " + str(tracker.get_reports(peer))
      G.add_node(peer)

    for peer in tracker.peer_list:
      for peer2 in tracker.peer_list:
        if peer != peer2:
          G.add_edge(peer, peer2)
    
    nx.draw(G, labels=labels, with_labels=True)

    while len(tracker.peer_list) == l and sum(reports.values()) == s:
      plt.pause(0.0001)

    l = len(tracker.peer_list)
    s = sum(reports.values())
    plt.clf()