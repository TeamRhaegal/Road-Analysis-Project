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
from threading import Thread


led = 22
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led,GPIO.OUT)
GPIO.output(led,True)
US2=0x001

count = 0




class MyUS(Thread):

    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus
        USAG=0
        USAD=0
        USAC=0

    def run(self):
        while True:
		    msg = self.bus.recv()
			time.sleep(0.5)			
			if msg.arbitration_id == US2:
				# ultrason arriere gauche
				distance = int.from_bytes(msg.data[0:2], byteorder='big')
				USAG = distance
				aff = "Gauche"+ str(USAG)
				print(aff)
				# ultrason arriere droit
				distance = int.from_bytes(msg.data[2:4], byteorder='big')
				USAD = distance
				aff = "Droit"+ str(USAD)
				print(aff)
				# ultrason avant centre
				distance = int.from_bytes(msg.data[4:6], byteorder='big')
				USAC = distance
				aff = "Droit"+ str(USAC)
				print(aff)
			
class MyCommand(Thread):

    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus

    def run(self):
        while True :
            msg = can.Message(arbitration_id=0x010,data=[0xBC,0x00,0x00, 0x00, 0x00, 0x00,0x00, 0x00],extended_id=False)
			bus.send(msg)

class MyEmergencyStop(Thread)	

	def __init__(self, bus):
		Thread.__init__(self)
		self.bus = bus
	
	def run(self):
		while True :
			msg = can.Message(arbitration_id=0x010,data=[0xBC,0x00,0x00, 0x00, 0x00, 0x00,0x00, 0x00],extended_id=False)
			bus.send(msg)
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
    #newsend = MyCommand(bus)
    #newsend.start()
    #newsend = MyEmergencyStop(bus)
    #newsend.start()
    

    threadUS.join()
    


except KeyboardInterrupt:
	#Catch keyboard interrupt
	GPIO.output(led,False)
	os.system("sudo /sbin/ip link set can0 down")
	print('\n\rKeyboard interrtupt')
