import random
import re
import sched
import socket
import sys
import threading
from time import sleep, time
import time
from config import *
import binascii

################
# 192.168.43.26
# socket.AF_INET, socket.SOCK_DGRAM


import random
import socket
import threading
from time import sleep
from config import *


class MyNetwork:

    def __init__(self):
        self.timer = None

        self.serverStack = [('', time.time())] * 20
         #FOR CRC
        self.CRC = '0110'

        self.stack = [('', None, '')] * 20
        self.counter = 0

        self.game_connection = socket.socket()        # UNITY TO SERVER
        self.game_socket = socket.socket()            # SERVER TO UNITY

        self.network_connection = socket.socket()     # CLIENT TO SERVER
        self.network_socket = socket.socket()         # SERVER TO CLIENT

        self.isServer = True

        self.game_socket.bind(('', 8001))
        self.game_socket.listen(5)

        self.network_socket.bind(('', 8000))          # SERVER TO CLIENT
        self.network_socket.listen(5)

        stackChecker = threading.Thread(target=self.checkStack)
        stackChecker.start()

    # ---------------------------- ! Dont Touch My Code ! ----------------------------
    # --------------------------------------------------------------------------------
    # -------------------------------------🏴‍☠️🏴‍☠️---------------------------------------
    # --------------------------------------------------------------------------------
    # -----------------------------🚩 ! Danger Zone ! 🚩-------------------------------

    def packetStore(self, packets):
        """Each packet contains -> data , pckt_time , ip
        """
        for _pckt in packets:

            data, pckt_time, ip = _pckt

            if DestroyPacket and random.randint(0, 100) < Chance_Destroy * 100:
                index_1 = random.randint(0, len(data) - 1)
                index_2 = random.randint(0, len(data) - 1)
                index_3 = random.randint(0, len(data) - 1)
                data = data.replace(data[index_1], data[index_2])
                data = data[:index_3] + '$' + data[index_3 + 1:]
                print("--- Packet Destroy ---")
                _pckt = (data , pckt_time, ip)

            if PacketLoss and random.randint(0, 100) < Chance_Loss * 100:
                print("--- Packet Loss ---")
                continue

            safe, pckt = self.Firewall(_pckt)
            if not safe:
                continue

            data, pckt_time, ip = pckt

            if self.counter >= max_stack_size:
                print("--- Stack Full ! ---")
                return

            self.stack[self.counter] = (data, pckt_time, ip)
            self.counter += 1

    def checkStack(self):
        while True:
            while self.counter > 0:
                sleep(network_delay)
                self.OnNetworkData()

    def ReadLastPacket(self):
        """Read last packet in stack.
            return -> content , pckt_time , ip
        """

        if self.counter > 0:
            result = self.stack[self.counter - 1]
            self.counter -= 1
            return result

    def SendDataToClient(self, data: str):
        """Send packet data to your Client using (self.network_connection)
        """

        try:
            data = str(self.encode_data_CRC(data))
            self.network_connection.send(data.encode())
        except BaseException as e:
            print(e)

    def SendDataToGame(self, data: str):
        """Send packet data to Game
        """

        try:
            self.game_connection.send(data.encode())
        except BaseException as e:
            print(e)
            print(self.game_connection.setsockopt())

    # -----------------------------🚩 ! Danger Zone ! 🚩-----------------------------
    # --------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------

    # ------------------------------ ❤ This is For You ❤ ----------------------------

    # ----------------------------  Bridge Service Functions -------------------------

    def Firewall(self, packet):
        if packet[2] != '127.0.0.1' and len(self.stack) != 0:  # client IP
            self.stack.pop()
        elif len(self.stack) != 0:
            data = packet[0]
            if data[0] == 'H' or data[0] == 'C':
                self.SendDataToClient('ACK')
                pass
            else:
                if self.data_integrity(data):
                    self.SendDataToClient('ACK')
                    return True, packet
                else:

                    self.SendDataToClient('NACK')
                    return False, packet


    def OnGameData(self, data: str):  # receive data from unity
        print(f"Unity Says: {data}")
        if data[0] == 'H' or data[0] == 'C':
            pass
        else:
            if self.data_integrity(data):
                if int(data[0]) == 1:
                    self.serverStack[0] = (data, time.time())
                    self.timer = threading.Timer(5.0, self.handle_PacketLoss)
                    self.timer.start()
                    self.SendDataToClient(data)
                self.SendDataToGame('OK')
            elif data == 'CLOSE':
                self.network_connection.close()
            else:
                self.SendDataToGame('FAIL')

    def handle_PacketLoss(self):
        self.resendData()
        self.timer = threading.Timer(5.0, self.handle_PacketLoss)
        self.timer.start()


    def resendData(self):
        data = self.serverStack[0][0]
        self.SendDataToClient(data)


    def OnNetworkData(self):  # receive data from network
        data = self.ReadLastPacket()
        print(f"Network Says: {str(data)}")

        self.SendDataToGame(data[0])

    def data_integrity(self, data):
        pattern1 = re.compile("[0-2],+")
        if bool(pattern1.match(data)) and not('$' in data):
            return True
        else:
            return False

    def CRC_Msg(self, data):
        data = data[0: len(data) - len(self.CRC) + 1]
        data = self.decode_bin_str(data)
        return data

    def Xor(self, a, b):
        result = []
        for i in range(1, len(b)):
            if a[i] == b[i]:
                result.append('0')
            else:
                result.append('1')
        return ''.join(result)

    def division(self, dividend, divisor):
        num = len(divisor)
        temp = dividend[0: num]
        while num < len(dividend):
            if temp[0] == '1':
                temp = self.Xor(divisor, temp) + dividend[num]
            else:  # If leftmost bit is '0'
                temp = self.Xor('0' * num, temp) + dividend[num]
            num += 1
        if temp[0] == '1':
            temp = self.Xor(divisor, temp)
        else:
            temp = self.Xor('0' * num, temp)
        return temp

    def encode_data_CRC(self, data2):
        l_CRC = len(self.CRC)
        data = self.encode_str_bin(data2)
        appended_data = data + '0' * (l_CRC - 1)
        remainder = self.division(appended_data, self.CRC)
        codeword = data + remainder
        return codeword

    def decode_data_CRC(self, data):
        if data:
            l_CRC = len(self.CRC)
            appended_data = data + '0' * (l_CRC - 1)
            remainder = self.division(appended_data, self.CRC)
            if int(remainder) == 0:
                return True
            else:
                return False

    def encode_str_bin(self, data):
        result = ""
        for i in range(0, len(data)):
            binary = '{0:08b}'.format(ord(data[i]))
            result = result + binary
        return result

    def decode_bin_str(self, data):
        result = ""
        for i in range(0, len(data), 8):
            c = chr(int(data[i:i + 8], 2))
            result = result + str(c)
        return result
