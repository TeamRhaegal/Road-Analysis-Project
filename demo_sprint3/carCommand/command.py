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
        CMD_V_A = 50
        CMD_Turbo = 75
        Temps_necessaire=0.01
        stopDetected = 0   #variable qui empeche d'envoyé un message infini à l'ihm quand un stop ets détecté
        searchDetected = 0 # de même pour le pnneau search
        while self.runEvent.isSet() :  #remplacer avec l'event du main
            
            while not(self.stopEvent.isSet()):
                CMD_O = 50
                CMD_V = 50
                CMD_V_A= 50
                CMD_Turbo = 75
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
    
                    R.lockWidthStop.acquire()
                    R.lockWidthSearch.acquire()
                    
                    widthStopSign = R.widthStop
                    widthSearchSign = R.widthSearch
                    
                    R.lockWidthStop.release()
                    R.lockWidthSearch.release()
                    
                    # envoie de message à l'ihm en fonction du panneau détecté ainsi que la commande à effectuer
                    if widthStopSign :
                        CMD_V_A = 50  
                        searchDetected = 0
                        if  not(stopDetected) :
                            constructMsgToIHM("sign","stop")
                            stopDetected = 1
                    elif widthSearchSign :
                        CMD_V_A = 60
                        stopDetected = 0
                        if  not(searchDetected) :
                            constructMsgToIHM("sign","search")
                            searchDetected = 1
                    else : 
                        CMD_V_A = 60
                        stopDetected = 0
                        searchDetected = 0
    
                    CMD_V = CMD_V + 0x80
                    CMD_O = CMD_O + 0x80
                    CMD_V_A = CMD_V_A + 0x80
                    
                    R.modeLock.acquire()
                    modeC = R.mode
                    R.modeLock.release()
                    
                    if modeC == "auto" and R.joystick == "none":
                        
                        if widthStopSign :  #changer sign width avec index 2 du panneau 
                            toSignDistance = (realSignWidth*focal)/widthStopSign #changer avec liste panneau index 2
                            Temps_necessaire = (toSignDistance / ((1.2/5)))-1  #calcul du temps à  attendre, -1 car temps reconnaissance = 1 sec
                            print(Temps_necessaire)
                        else :  Temps_necessaire = 0.01
                        
                        # condition du stop pour marquer un arrêt
                       
                        msg = can.Message(arbitration_id=MOT,data=[CMD_V_A, CMD_V_A, 0x00,0,0,0,0,0],extended_id=False)
                        time.sleep(Temps_necessaire)
                        self.bus.send(msg)
                        #si c'est un panneau stop attendre 5 secondes à l'arrêt
                        if widthStopSign :
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
                        
                    
                else:
                    msg = can.Message(arbitration_id=MOT,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
                    self.bus.send(msg)
                time.sleep(0.1)
            msg = can.Message(arbitration_id=MOT,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
            self.bus.send(msg)
            
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
        emergencyOn = 0
        emergencyOff = 0
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
                

                if UFL<MAX_DISTANCE_US or UFR<MAX_DISTANCE_US or UFC<MAX_DISTANCE_US:
                    self.stopEvent.set()
                    emergencyOff = 0
                    #envoi de message aussi
                    if  not(emergencyOn)  :
                        constructMsgToIHM("urgent","on")
                        emergencyOn = 1
                else : 
                    emergencyOn = 0
                    self.stopEvent.clear()
                    if not(emergencyOff) :
                        constructMsgToIHM("urgent","off")
                        emergencyOff = 1
            time.sleep(0.01)
