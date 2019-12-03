# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 15:07:13 2019

@author: Nicolas
"""

import can
import time
from threading import Thread
import sharedRessources as R



MOT=0x010     #identifiant commande moteur CAN
US2=0x001      #identifiant Ultrasons arrière CAN
US1=0x000      ##identifiant Ultrasons arrière CAN
MS=0x100
MAX_DISTANCE_US = 15





			
class MyCommand(Thread):

    def __init__(self, bus,runEvent,stopEvent):
        Thread.__init__(self)
        self.bus = bus
        self.runEvent= runEvent
        self.stopEvent = stopEvent

    def run(self):
       
		# mettre la condition de detection d'obstacle ultrasons
        realSignWidth = 0.20  #nb à déterminer en cm
        focal = 1026
        CMD_O = 50
        CMD_V = 50
        CMD_V_A=50
        CMD_Turbo = 75
        Temps_necessaire=0.01
        while self.runEvent.isSet() :  #remplacer avec l'event du main
            
            CMD_O = 50
            CMD_V = 50
            CMD_V_A= 50
            CMD_Turbo = 75
            signC="none"
            R.lockConnectedDevice.acquire()
            check_connected = R.connectedDevice
            R.lockConnectedDevice.release()
            #print(check_connected)
            if(check_connected == True):           
                    
                #affectation des valeurs pour le mode assissté en fonction des commandes reçues
                R.turboLock.acquire()
                R.joystickLock.acquire()
                if R.turbo == "on" : CMD_Turbo = 100
                if R.turbo == "off" : CMD_Turbo = 75
                if R.joystick == "right" :  
                    CMD_O = 100
                    CMD_V= 50
                if R.joystick == "left" : 
                    CMD_O = 0
                    CMD_V = 50
                if R.joystick == "front" : 
                    CMD_V = CMD_Turbo
                    CMD_O = 50
                if R.joystick == "right&front" : 
                    CMD_O = 100
                    CMD_V = CMD_Turbo
                if R.joystick == "left&front" :
                    CMD_O = 0
                    CMD_V = CMD_Turbo
                if R.joystick == "none" : 
                    CMD_V = 50
                    CMD_O = 50

                R.turboLock.release()
                R.joystickLock.release()   
                
                #affectation du type de panneau reconnu ainsi que de sa largeur en pixel
                R.signDetectionLock.acquire()
                if len(R.signDetection):
                    for i in len(R.signDetection) :
                        
                        if R.signDetection[i][0] == "stop":
                            signC = R.signDetection[i][0]  #uniquement si le panneau reconnu est un stop : on réagit
                            signWidth = R.signDetection[i][1] #☺ on récupère la largeur en pixel du panneau
                            del R.signDetection[i]
                        i=i+1
                R.signDetectionLock.release()
                
                if signC == "stop" : CMD_V_A = 50  # si panneu stop reconnu ou search aussi ?
                else : CMD_V_A = 60

                CMD_V = CMD_V + 0x80
                CMD_O = CMD_O + 0x80
                CMD_V_A = CMD_V_A + 0x80
                
                R.modeLock.acquire()
                modeC = R.mode
                R.modeLock.release()
                if modeC == "auto" and R.joystick == "none":
                
                    
                    if signWidth and signC == "stop":  #changer sign width avec index 2 du panneau 
                        toSignDistance = (realSignWidth*focal)/signWidth  #changer avec liste panneau index 2
                        Temps_necessaire = (toSignDistance / ((1.2/5)))-1  #calcul du temps à  attendre, -1 car temps reconnaissance = 1 sec
                        print(Temps_necessaire)
                    else :  Temps_necessaire = 0.01
                    
                    # condition du stop pour marquer un arrêt
                   
                    msg = can.Message(arbitration_id=MOT,data=[CMD_V_A, CMD_V_A, 0x00,0,0,0,0,0],extended_id=False)
                    time.sleep(Temps_necessaire)
                    self.bus.send(msg)
                    #si c'est un panneau stop attendre 5 secondes à l'arrêt
                    if signC == "stop":
                        time.sleep(5)
                  '''  # condition du search mode détecté
                    if signC == "search" : 
                        msg = can.Message(arbitration_id=MOT,data=[CMD_V_A, CMD_V_A, 0x00,0,0,0,0,0],extended_id=False)
                        time.sleep(Temps_necessaire)
                        self.bus.send(msg)
                        time.sleep(2)
                        msg = can.Message(arbitration_id=MOT,data=[0, 0, 0x00,0,0,0,0,0],extended_id=False)
                        time.sleep(10)
                        self.bus.send(msg)
                     '''   

                elif modeC == "assist" :
                    # comande en fonction des messages de l'ihm
                    msg = can.Message(arbitration_id=MOT,data=[CMD_V, CMD_V, CMD_O,0,0,0,0,0],extended_id=False)
                    self.bus.send(msg)
                    
                    
                # gestion des obstacles : Emergency STOP    
                elif self.stopEvent.isSet() :
                    msg = can.Message(arbitration_id=MOT,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
                    time.sleep(0.01)
                    self.bus.send(msg)
                    self.stopEvent.clear()
                
            else:
                msg = can.Message(arbitration_id=MOT,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
                self.bus.send(msg)

            time.sleep(0.1)
        msg = can.Message(arbitration_id=MOT,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
        self.bus.send(msg)
                
class MySensor(Thread):

    def __init__(self, bus, runEvent,stopEvent):
        Thread.__init__(self)
        self.bus = bus
        self.runEvent = runEvent
        self.stopEvent = stopEvent

    def run(self):
        URL = 180
        URR = 180
        URC = 180
        UFL = 180
        UFR = 180
        UFC = 180
        wheelPerimeter = 0.19 *2*3.14  
        while self.runEvent.isSet() :
            
            R.lockConnectedDevice.acquire()
            check_connected = R.connectedDevice
            R.lockConnectedDevice.release()
        
            if (check_connected == True):
                
                msg = self.bus.recv()
                time.sleep(0.01)
                """if msg.arbitration_id == MS:
                    Batmes = int(str(msg.data[2:4]).encode('hex'), 16)
                    U = (4095 / Batmes) * (3.3 / 0.2)
                    print(Batmes)"""
                if msg.arbitration_id == MS:
                    # Vitesse voiture
                    wheel_speed = int(str(msg.data[6:8]).encode('hex'), 16)
                    R.wheelSpeed = (0.01*wheel_speed*wheelPerimeter / 60) #metre/s max : 1.21 m/s donc 4,34 km/H
                    #message = "Vitesse :" + str(wheelSpeed)+ ";"
                    #print(message)
                    '''
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
                    '''
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
                

                if UFL<MAX_DISTANCE_US or UFR<MAX_DISTANCE_US or UFC<MAX_DISTANCE_US: self.stopEvent.set()

                
            time.sleep(0.05)
