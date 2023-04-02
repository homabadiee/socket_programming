import random
import string
from time import sleep
import time
from config import DDoS , Chance_DDoS , pcktCount
from network import MyNetwork

def _ip():
    numbers = string.digits.replace('0' , '')

    ip = ''.join(random.choice(numbers) for i in range(3))
    ip += '.'
    ip += ''.join(random.choice(numbers) for i in range(3))
    ip += '.'
    ip += ''.join(random.choice(numbers) for i in range(3))
    ip += '.'
    ip += ''.join(random.choice(numbers) for i in range(3))

    return ip

def randomstr(length):
    players = '12'
    cell = '012'

    result_str = ''.join(random.choice(players))
    result_str += ','
    result_str += ''.join(random.choice(cell))
    result_str += ','
    result_str += ''.join(random.choice(cell))

    return result_str
    
def DDoSAttack(myNetwork : MyNetwork):
  while True:
    sleep(1)
    if DDoS and random.randint(0 , 100) < Chance_DDoS * 100:
        myip = _ip()
        datas = []
        print("--- DDoS Attack :) ---")
        for i in range(pcktCount):
            datas.append((str(randomstr(15)) , time.time() , myip))
            sleep(random.random() * 0.2)

        myNetwork.packetStore(datas)
      