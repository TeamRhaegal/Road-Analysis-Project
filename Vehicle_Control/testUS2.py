#!/usr/bin/python3
#
# simple_tx_test.py
#
# This python3 sent CAN messages out, with byte 7 increamenting each time.
# For use with PiCAN boards on the Raspberry Pi
# http://skpang.co.uk/catalog/pican2-canbus-board-for-raspberry-pi-2-p-1475.html
#
# Make sure Python-CAN is installed first http://skpang.co.uk/blog/archives/1220
#
# 01-02-16 SK Pang
#
#
#


import RPi.GPIO as GPIO
import can
import time
import os
import struct
from threading import Thread, Lock




US2=0x001
US1=0x000

led=22
DistanceMaxUS = 15

ObstacleFrontLock= Lock()
ObstacleRearLock = Lock()

ObstacleRear = 0
ObstacleFront = 0


class MyUS(Thread):

    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus


    def run(self):
        while True :
            msg = self.bus.recv()
            time.sleep(0.01)
            if msg.arbitration_id == US2:
                # ultrason arriere gauche
                distance = int.from_bytes(msg.data[0:2], byteorder='big')
                URL = distance
                message = "URL:" + str(distance)+ ";"
                #print(message)
                # ultrason arriere droit
                distance = int.from_bytes(msg.data[2:4], byteorder='big')
                URR = distance
                message = "URR:" + str(distance)+ ";"
                #print(message)
                # ultrason arriere centre
                distance = int.from_bytes(msg.data[4:6], byteorder='big')
                URC = distance
                message = "UFC:" + str(distance)+ ";"
                #print(message)
                print("---------")
            if msg.arbitration_id == US1:
                # ultrason avant gauche
                distance = int.from_bytes(msg.data[0:2], byteorder='big')
                UFL = distance
                message = "UFL:" + str(distance)+ ";"
                print(message)
                # ultrason avant droit
                distance = int.from_bytes(msg.data[2:4], byteorder='big')
                UFR = distance
                message = "UFR:" + str(distance)+ ";"
                #print(message)
                # ultrason avant centre
                distance = int.from_bytes(msg.data[4:6], byteorder='big')
                UFC = distance
                message = "UFC:" + str(distance)+ ";"
                #print(message)
                print("---------")
            
            ObstacleFrontLock.acquire()
            ObstacleRearLock.acquire()
            if  URL <15 or URR<15 or URC <15: ObstacleRear = 1
            else : ObstacleRear = 0 
            if UFL<15 or UFR<15 or UFC<15: ObstacleFront = 1
            else: ObstacleFront = 0 
            ObstacleFrontLock.release()
            ObstacleRearLock.release()
                

			
class MyCommand(Thread):

    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus

        

    def run(self):
		
		# mettre la condition de detection d'obstacle ultrasons
        while True :
            ObstacleFrontLock.acquire()
            ObstacleRearLock.acquire()
            if ObstacleRear or ObstacleFront :
                print("OU LA **************************************")
                msg = can.Message(arbitration_id=0x010,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
                time.sleep(0.02)
                self.bus.send(msg)
                break
            else :
                print("coooooooooooooooooooooooooooooooooooooooooooooooooooooool")
                msg = can.Message(arbitration_id=0x010,data=[0x00, 0x00, 0xBC,0,0,0,0,0],extended_id=False)
                self.bus.send(msg)
                time.sleep(0.02)
            ObstacleFrontLock.release()
            ObstacleRearLock.release()
            msg = can.Message(arbitration_id=0x010,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
            time.sleep(0.01)
            self.bus.send(msg)
                

                
   
	#inserer ici un mutex pour chaque variable d'ultrasons

print('\n\rCAN Rx test')
print('Bring up CAN0....')

# Bring up can0 interface at 500kbps
os.system("sudo /sbin/ip link set can0 up type can bitrate 400000")
time.sleep(0.1)
print('Press CTL-C to exit')
try:
	bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
except OSError:
	print('Cannot find PiCAN board.')
	GPIO.output(led,False)
	exit()
	
# Main loop
try:
    threadUS = MyUS(bus)
    threadUS.start()
    threadcom = MyCommand(bus)
    threadcom.start()
    

    threadUS.join()
    threadcom.join()
    


except KeyboardInterrupt:
	#Catch keyboard interrupt
	os.system("sudo /sbin/ip link set can0 down")
	print('\n\rKeyboard interrtupt')
