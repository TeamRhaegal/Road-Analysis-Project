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



MOT=0x010     #identifiant commande moteur CAN
US2=0x001      #identifiant Ultrasons arrière CAN
US1=0x000      ##identifiant Ultrasons arrière CAN


led=22

#variables globales
Turbo ="off"
Joystick = "none"
Mode = "assisted"    #auto pour test unitaire
Deconnexion = "off"
Panneau = "none"
NbPixel = "0"
vitesseRoue = 50
DistanceMaxUS = 15
ObstacleRear = 0
ObstacleFront = 0


ModeLock =Lock()
JoystickLock = Lock()
TurboLock = Lock()
PanneauLock = Lock()
NbPixelLock = Lock()
VitesseLock = Lock()
ObstacleFrontLock= Lock()
ObstacleRearLock = Lock()



			
class MyCommand(Thread):

    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus

    def run(self):
       
		# mettre la condition de detection d'obstacle ultrasons
        Width_panneau = 0.20  #nb à déterminer
        Focal = 595
        while True : 
            
            ModeLock.acquire()
            TurboLock.acquire()
            JoystickLock.acquire()
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
    
            ModeLock.release()
            TurboLock.release()
            JoystickLock.release()   
            
            PanneauLock.acquire()
            if Panneau == "num panneau": CMD_V_A = 0  #panneau lock
            else : CMD_V_A = 0xB6
            PanneauLock.release()
            CMD_V = CMD_V + 0x10
            CMD_O = CMD_O + 0x10
                
            if Mode == "auto":
                
                NbPixelLock.acquire()
                VitesseLock.acquire()
                if NbPixel != 0 or CMD_V_A== 0 :
                    Distance_panneau = (Width_panneau*Focal)/NbPixel
                    Temps_necessaire = Distance_panneau / vitesseRoue   #calcul du temps à  attendre 
                else :  Temps_necessaire = 0.01
                NbPixelLock.release()
                VitesseLock.release()
                
                    
                msg = can.Message(arbitration_id=0x010,data=[CMD_V_A, CMD_V_A, 0x00,0,0,0,0,0],extended_id=False)
                time.sleep(Temps_necessaire)
                self.bus.send(msg)
                #mode autonome
                
            elif Mode == "assisted" :
                msg = can.Message(arbitration_id=0x010,data=[CMD_V, CMD_V, CMD_O,0,0,0,0,0],extended_id=False)
                time.sleep(0.01)
                self.bus.send(msg)
            # gestion des obstacles : Emergency STOP    
            elif ObstacleRear or ObstacleFront :
                msg = can.Message(arbitration_id=0x010,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
                time.sleep(0.01)
                self.bus.send(msg)
                
                
class MySensor(Thread):

    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus

    def run(self):
        Perimetre_roue = 0.62
        while True :
            msg = self.bus.recv()
            
            if msg.arbitration_id == US2:
                # Vitesse voiture
                VitesseLock.acquire()
                vitesseRoue = int.from_bytes(msg.data[4:6], byteorder='big')
                vitesseRoue = (100*vitesseRoue*Perimetre_roue / 60) #metre/s
                VitesseLock.release()
                message = "Vitesse :" + str(vitesseRoue)+ ";"
                #print(message)
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
                #print(message)
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

    threadsense = MySensor(bus)
    threadcom = MyCommand(bus)
    threadcom.start()
    threadsense.start()
    
    threadcom.join()
    threadsense.join()
    


except KeyboardInterrupt:
	#Catch keyboard interrupt
	os.system("sudo /sbin/ip link set can0 down")
	print('\n\rKeyboard interrtupt')