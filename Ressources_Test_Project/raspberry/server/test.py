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
from threading import Thread


led = 22
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led,GPIO.OUT)
GPIO.output(led,True)
US2=0x001

count = 0

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
	i=0
	while i<5:
		GPIO.output(led,True)
		msg = can.Message(arbitration_id=0x010,data=[0x00,0x00,0x00, 0x00, 0x00, 0x00,0x00, 0x00],extended_id=False)
		bus.send(msg)
		count +=1
		time.sleep(0.1)
		GPIO.output(led,False)
		time.sleep(0.1)
		print(count)
		i+=1
	msg = can.Message(arbitration_id=0x010,data=[0x00,0x00,0x00, 0x00, 0x00, 0x00,0x00, 0x00],extended_id=False)
	bus.send(msg)
	msg = bus.recv()

	#print(msg.arbitration_id, msg.data)

	if msg.arbitration_id == US2:
		# ultrason arriere gauche
		distance = int.from_bytes(msg.data[0:2], byteorder='big')
		message = "URL:" + str(distance)+ ";"
		print(message);
		# ultrason arriere droit
		distance = int.from_bytes(msg.data[2:4], byteorder='big')
		message = "URR:" + str(distance)+ ";"
		print(message)
		# ultrason avant centre
		distance = int.from_bytes(msg.data[4:6], byteorder='big')
		message = "UFC:" + str(distance)+ ";"
		print(message)



except KeyboardInterrupt:
	#Catch keyboard interrupt
	GPIO.output(led,False)
	os.system("sudo /sbin/ip link set can0 down")
	print('\n\rKeyboard interrtupt')
