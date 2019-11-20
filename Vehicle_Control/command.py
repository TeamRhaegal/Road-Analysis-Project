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
MS=0x100

led=22

#variables globales
Turbo ="off"
Joystick = "none"
Mode = "auto"    #auto pour test unitaire
Deconnexion = "off"
Panneau = "none"
NbPixel = 10
vitesseRoue = 0
DistanceMaxUS = 10
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
        CMD_O = 50
        CMD_V = 50
        CMD_V_A=50
        Temps_necessaire=0.01
        while True : 
            time.sleep(0.01)            
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
            if Panneau == "num panneau": CMD_V_A = 50  #panneau lock
            else : CMD_V_A = 100
            PanneauLock.release()
            CMD_V = CMD_V + 0x80
            CMD_O = CMD_O + 0x80
            CMD_V_A = CMD_V_A + 0x00
            if Mode == "auto":
                
                NbPixelLock.acquire()
                VitesseLock.acquire()
                if NbPixel != 0 or CMD_V_A == 0 :
                    Distance_panneau = (Width_panneau*Focal)/NbPixel
                    Temps_necessaire = Distance_panneau / (vitesseRoue+0.00001)   #calcul du temps à  attendre 
                else :  Temps_necessaire = 0.01
                NbPixelLock.release()
                VitesseLock.release()
                

                msg = can.Message(arbitration_id=MOT,data=[CMD_V_A, CMD_V_A, 0x00,0,0,0,0,0],extended_id=False)
                time.sleep(Temps_necessaire)
                self.bus.send(msg)
                #mode autonome
               
            elif Mode == "assisted" :
                msg = can.Message(arbitration_id=MOT,data=[CMD_V, CMD_V, CMD_O,0,0,0,0,0],extended_id=False)
                time.sleep(0.01)
                self.bus.send(msg)
            # gestion des obstacles : Emergency STOP    
            elif ObstacleRear or ObstacleFront :
                msg = can.Message(arbitration_id=MOT,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
                time.sleep(0.01)
                self.bus.send(msg)
            
                
                
class MySensor(Thread):

    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus

    def run(self):
        Perimetre_roue = 0.19 *2*3.14  
        while True :
            msg = self.bus.recv()
            time.sleep(0.01)
            if msg.arbitration_id == MS:
                Batmes = int.from_bytes(msg.data[2:4], byteorder='big')
                U = (4095 / Batmes) * (3.3 / 0.2)
                print(Batmes)
            if msg.arbitration_id == MS:
                # Vitesse voiture
                VitesseLock.acquire()
                vitesseRoue = int.from_bytes(msg.data[4:6], byteorder='big')
                vitesseRoue = (0.01*vitesseRoue*Perimetre_roue / 60) #metre/s max : 1.21 m/s donc 4,34 km/H
                VitesseLock.release()
                message = "Vitesse :" + str(vitesseRoue)+ ";"
                print(message)
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
            '''
            ObstacleFrontLock.acquire()
            ObstacleRearLock.acquire()
            if  URL <DistanceMaxUS or URR<DistanceMaxUS or URC <DistanceMaxUS: ObstacleRear = 1
            else : ObstacleRear = 0 
            if UFL<DistanceMaxUS or UFR<DistanceMaxUS or UFC<DistanceMaxUS: ObstacleFront = 1
            else: ObstacleFront = 0 
            ObstacleFrontLock.release()
            ObstacleRearLock.release()
            '''
            
           
                

                
   
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
    msg = can.Message(arbitration_id=MOT,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
    bus.send(msg)
    time.sleep(5)
    os.system("sudo /sbin/ip link set can0 down")
    print('\n\rKeyboard interrtupt')
