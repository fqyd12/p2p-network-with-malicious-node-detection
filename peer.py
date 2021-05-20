import sys
import os
from utils import create_socket
from constants import TRACKER_PORT, REPORTS_SOCK_PORT, malicious_words
import threading
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

class Peer:
  def __init__(self, port):
    self.port = port

    self.total = 0
    self.m_recv = {}
    self.n_recv = {}

    self.is_alive = True

    sock = create_socket()
    sock.connect(('127.0.0.1', TRACKER_PORT))

    num_peer_ports = int(sock.recv(5).decode("utf-8"))

    if num_peer_ports > 1:
      peer_ports_str = sock.recv(num_peer_ports).decode('utf-8')
      peer_ports = peer_ports_str.split(",")

      print("Received peer list", peer_ports)

      # for peer_port in peer_ports:
      #   if peer_port:
      #     self.connect_to(int(peer_port))

    server_sock = create_socket()
    print("Creating peer on port: ",port)
    server_sock.bind(('', port))
    server_sock.listen(1)

    self.server_sock = server_sock

    sock.send(str(port).encode("utf-8"))

    self.incoming_connection_thread = threading.Thread(target=self.handle_incoming_connection)
    self.incoming_connection_thread.start()

  def handle_incoming_connection(self):
    while True:
      try:
        incoming_peer_sock, incoming_peer_addr = self.server_sock.accept()

        msg_len = incoming_peer_sock.recv(5).decode('utf-8')
        if msg_len == 'quitt':
          print("Quitting.")
          break
        msg_len = int(msg_len)

        msg = incoming_peer_sock.recv(msg_len).decode('utf-8')

        sender_port, msg = self.extract_msg(msg)

        print("Recevied:", msg, "from", sender_port)

        self.total += 1

        if sender_port in self.n_recv:
          self.m_recv[sender_port] += self.is_malicious(msg)
        else:
          self.m_recv[sender_port] = self.is_malicious(msg)

        if sender_port in self.n_recv:
          self.n_recv[sender_port] += 1
        else:
          self.n_recv[sender_port] = 1

        w1 = self.n_recv[sender_port]/self.total
        w2 = self.m_recv[sender_port]/self.n_recv[sender_port]

        belief = 0.3*w1 + 0.7*w2

        if belief >= 0.8:
          print("Reporting", sender_port, "to tracker for malicious activity.")
          sock = create_socket()
          sock.connect(('127.0.0.1', REPORTS_SOCK_PORT))

          sock.send(str(sender_port).zfill(5).encode('utf-8'))

        incoming_peer_sock.close()
      except KeyboardInterrupt:
        break
    os._exit(1)

  def connect_to(self, port):
    sock = create_socket()
    sock.connect(('127.0.0.1', port))
  
  def attach_headers(self, msg):
    headers = str(self.port).zfill(5) + "\n<--headers_finished-->"
    return headers+msg
  
  def extract_msg(self, msg):
    headers, msg = msg.split("<--headers_finished-->")
    sender_port = headers.split("\n")[0]

    return int(sender_port), msg

  def is_malicious(self, msg):
    for malicious_word in malicious_words:
      if msg in malicious_word:
        return 1
    
    return 0

  def send(self, port, msg):
    sock = create_socket()
    sock.connect(('127.0.0.1', int(port)))

    msg = self.attach_headers(msg)
    msg_len = str(len(msg)).zfill(5)

    sock.send(msg_len.encode('utf-8'))

    sock.send(msg.encode('utf-8'))

if __name__ == "__main__":
  port = int(sys.argv[1])
  peer = Peer(port)
  print("Hi Peer",port)
  print("Port:Message and enter to send Message(max 20 characters) to Port")
  while True:
    port, msg = input().split(":")
    peer.send(port, msg)
