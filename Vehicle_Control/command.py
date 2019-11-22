# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 15:07:13 2019

@author: Nicolas
"""

import RPi.GPIO as GPIO
import can
import time
import os
import struct
from threading import Thread, Lock
from queue import Queue



MOT =0x010     #identifiant commande moteur CAN
US2=0x001      #identifiant Ultrasons arrière CAN
US1=0x000      ##identifiant Ultrasons arrière CAN

Width_panneau = 0.20  #nb à déterminer
Focal = 595
Perimetre_roue = 62.8

Turbo ="off"
Joystick = "none"
Mode = "assisted"
Deconnexion = "off"
Panneau = "none"
Nb_pixel = "0"

Mode_Lock =Lock()
Joystick_Lock = Lock()
Turbo_Lock = Lock()
Panneau_Lock = Lock()
Nb_pixel_Lock = Lock()
Vitesse_Lock = Lock()


			
class MyCommand(Thread):

    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus

    def run(self):
       
		# mettre la condition de detection d'obstacle ultrasons
        Mode_Lock.acquire()
        Turbo_Lock.acquire()
        Joystick_Lock.acquire()
        while True : 
            if Turbo == "on" : CMD_Turbo = 100
            if Turbo == "off" : CMD_Turbo = 75
            if Joystick == "right" :  CMD_O = 100
            if Joystick == "left" : CMD_O = 0
            if Joystick == "front" : CMD_V = CMD_Turbo
            if Joystick == "right" : CMD_O = 100
            if Joystick == "right&front" : 
                CMD_O = 100
                CMD_V = CMD_Turbo
            if Joystick == "left&front" :
                CMD_O = 0
                CMD_V = CMD_Turbo
    
            Mode_Lock.release()
            Turbo_Lock.release()
            Joystick_Lock.release()   
            
            if Panneau == "num panneau": CMD_V_A = 0  #panneau lock
            else : CMD_V_A = 0xB6
            
            CMD_V = CMD_V + 0x10
            CMD_O = CMD_O + 0x10
                
            if Mode == "auto":
                
                Nb_pixel_Lock.acquire()
                Vitesse_Lock.acquire()
                if Nb_pixel != 0:
                    Distance_panneau = (Width_panneau*Focal)/Nb_pixel
                    Temps_necessaire = Distance_panneau / vitesse
                    #calcul du temps à  attendre  
                    
                Nb_pixel_Lock.release()
                Vitesse_Lock.release()
                    
                msg = can.Message(arbitration_id=0x010,data=[CMD_V_A, CMD_V_A, 0x00,0,0,0,0,0],extended_id=False)
                time.sleep(0.01)
                self.bus.send(msg)
                #mode autonome
                
            elif Mode == "assisted" :
                msg = can.Message(arbitration_id=0x010,data=[CMD_V, CMD_V, CMD_O,0,0,0,0,0],extended_id=False)
                time.sleep(0.01)
                self.bus.send(msg)
                
            elif Deconnexion == "on" :
                msg = can.Message(arbitration_id=0x010,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
                time.sleep(0.01)
                self.bus.send(msg)
 class MySensor(Thread):

    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus

    def run(self):
       
		 while True :
            msg = self.bus.recv()
            
            if msg.arbitration_id == US2:
                # ultrason arriere gauche
                Vitesse_Lock.acquire()
                vitesse = int.from_bytes(msg.data[4:6], byteorder='big')
                vitesse = (100*vitesse*0.62 / 60) #metre/s
                Vitesse_Lock.release()
                message = "Vitesse :" + str(distance)+ ";"
                #print(message)
            
           
                

                
   
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
    queue_mode = Queue()
    queue_joystick = Queue()
    queue_turbo = Queue()

    threadcom = MyCommand(bus)
    threadcom.start()
    
    threadcom.join()
    


except KeyboardInterrupt:
	#Catch keyboard interrupt
	os.system("sudo /sbin/ip link set can0 down")
	print('\n\rKeyboard interrtupt')