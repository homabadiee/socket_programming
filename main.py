import threading
import time			
from network import MyNetwork
from DDoS import DDoSAttack

myNetwork = MyNetwork()

print ("Unity Socket is listening")

def GameDataReceive():  # receive game data & set in game
  while True:
    try:
      global myNetwork
      data = myNetwork.game_connection.recv(1024).decode()
      myNetwork.OnGameData(str(data))

    except BaseException as e:
      print (e)

      myNetwork.game_connection, addr = myNetwork.game_socket.accept()
      print (f"Game Connected \n {myNetwork.game_connection}\n")


def main():
  global myNetwork

  x = threading.Thread(target=GameDataReceive)
  x.start()

  xD = threading.Thread(target=DDoSAttack , args=(myNetwork,))
  xD.start()

  while True:
    try:
      data = myNetwork.network_connection.recv(1024).decode()

      if myNetwork.decode_data_CRC(data):
          data = myNetwork.CRC_Msg(data)
      if data == 'ACK':

          myNetwork.timer.cancel()

      elif data == 'NACK':
          myNetwork.timer.cancel()
          myNetwork.resendData()

      elif data:
          myNetwork.packetStore([(str(data), time.time(), "127.0.0.1")])

    except BaseException as e:
      print(e)
      if myNetwork.isServer:
        myNetwork.network_connection, addr = myNetwork.network_socket.accept()
        print("A Device connected")


if __name__ == "__main__":
  main()
