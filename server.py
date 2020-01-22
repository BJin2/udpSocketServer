import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json

clients_lock = threading.Lock()
connected = 0

#indexed by ip and port
clients = {}

def connectionLoop(sock):
   while True:
      data, addr = sock.recvfrom(1024)
      data = str(data)
      #if the address from socket is already in the client list
      #iwhich means the client is alreday connected
      if addr in clients:
         if 'heartbeat' in data:
            clients[addr]['lastBeat'] = datetime.now()
      else:
         if 'connect' in data:
            #If the request from the client is connect
            print(" ")
            print("New client connected")
            print(" ")
            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['color'] = 0
            message = {"cmd": 0,"player":[{"id":str(addr)}]}
            connectedClients = {"cmd": 3, "player": []}
            m = json.dumps(message)
            for c in clients:
               sock.sendto(bytes(m,'utf8'), (c[0],c[1]))
               connectedClients['player'].append({"id":str(c)})
            m = json.dumps(connectedClients)
            sock.sendto(bytes(m,'utf8'), (addr[0],addr[1]))

def cleanClients(sock):
   while True:
      message = {"cmd": 2,"player":[]}
      anyDropped = False
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            anyDropped = True
            print('Dropped Client: ', c)
            message['player'].append({"id":str(c)})
            clients_lock.acquire()
            del clients[c]
            clients_lock.release()
      if anyDropped:
         m = json.dumps(message)
         for c in clients:
               sock.sendto(bytes(m,'utf8'), (c[0],c[1]))
      time.sleep(1)

def gameLoop(sock):
   while True:
      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      print (clients)
      for c in clients:
         player = {}
         clients[c]['color'] = {"R": random.random(), "G": random.random(), "B": random.random()}
         player['id'] = str(c)
         player['color'] = clients[c]['color']
         GameState['players'].append(player)
      s=json.dumps(GameState)
      print(s)
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()
      time.sleep(1)

def main():
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,(s,))
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()
