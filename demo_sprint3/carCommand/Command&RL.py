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

        self.speed_cmd = 0
        self.movement = 0
        self.turn = 0
        self.enable_steering = 0
        self.enable = 0

    def run(self):
       
		# mettre la condition de detection d'obstacle ultrasons
        realSignWidth = 0.20  #nb à déterminer en cm
        focal = 342
        self.speed_cmd = 0
        self.movement = 0
        self.turn = 0
        self.enable_steering = 0
        self.enable_speed = 0
        CMD_O = 50
        CMD_V = 50
        CMD_V_A = 50
        CMD_V_AS = 50
        CMD_Turbo = 75
        Temps_necessaire=99999999999
        stopDetected = 0   #variable qui empeche d'envoyé un message infini à l'ihm quand un stop ets détecté
        searchDetected = 0 # de même pour le pnneau search
        countStop = 0
        timeNeedOK = 0
        while self.runEvent.isSet() :  #remplacer avec l'event du main
            while not(self.stopEvent.isSet()):
                CMD_O = 50
                CMD_V = 50
                CMD_V_A= 65
                CMD_Turbo = 75
                R.lockConnectedDevice.acquire()
                check_connected = R.connectedDevice
                R.lockConnectedDevice.release()
                #print(check_connected)
                if(check_connected == True):  
                    #affectation des valeurs pour le mode assissté en fonction des commandes reçues
                    R.turboLock.acquire()
                    R.joystickLock.acquire()
                    tempJoystick = R.joystick
                    tempTurbo = R.turbo
                    R.turboLock.release()
                    R.joystickLock.release()
                    
                    
                    if tempTurbo == "on" :
                        CMD_Turbo = 75
                    if tempTurbo == "off" :
                        CMD_Turbo = 65
                    if tempJoystick == "right" :  
                        CMD_O = 100 + 0x80
                        CMD_V= 50 
                    if tempJoystick == "left" : 
                        CMD_O = 0 + 0x80
                        CMD_V = 50
                    if tempJoystick == "front" : 
                        CMD_V = CMD_Turbo + 0x80
                        CMD_O = 50 
                    if tempJoystick== "right&front" :
                        self.turn = -1
                        self.enable_steering = 1
                        self.movement = 1
                        self.enable_speed = 1
                        #CMD_O = 70 + 0x80
                        #CMD_V = CMD_Turbo+ 0x80
                    if tempJoystick == "left&front" :
                        self.turn = 1
                        self.enable_steering = 1
                        self.movement = 1
                        self.enable_speed = 1
                        #CMD_O = 20+ 0x80
                        #CMD_V = CMD_Turbo+ 0x80
                    if tempJoystick == "none" : 
                        CMD_V = 50
                        CMD_O = 50

                    if self.enable_speed:
                        CMD_V = (50 + self.movement*self.speed_cmd) | 0x80
                    else:
                        CMD_V = (50 + self.movement*self.speed_cmd) & ~0x80

                    if self.enable_steering:
                        CMD_O = 50 + self.turn*30 | 0x80
                    else:
                        CMD_O = 50 + self.turn*30 & 0x80
                  
                    
                    R.lockWidthStop.acquire()
                    R.lockWidthSearch.acquire()
                    
                    widthStopSign = R.widthStop
                    widthSearchSign = R.widthSearch
                    
                    R.lockWidthStop.release()
                    R.lockWidthSearch.release()
                    
                    # envoie de message à l'ihm en fonction du panneau détecté ainsi que la commande à effectuer
                    if widthStopSign :
                        #searchDetected = 0
                        if  not(stopDetected) :
                            print("ouui y a un stop"+ str(searchDetected))
                            R.constructMsgToIHM("sign","stop")
                            stopDetected = 1
                            countStop = 0
                    elif widthSearchSign :
                        CMD_V_A = 65
                        #stopDetected = 0
                        if  not(searchDetected) :
                            print("ouui y a un search" + str(stopDetected))
                            R.constructMsgToIHM("sign","search")
                            searchDetected = 1
                    else : 
                        CMD_V_A = 65
                        stopDetected = 0
                        searchDetected = 0
    
                    CMD_V_A = CMD_V_A + 0x80
                    
                    R.modeLock.acquire()
                    modeC = R.mode
                    R.modeLock.release()
                    print("mode :" + modeC)
                    if modeC == "auto" and R.joystick == "none":
                        print("stopt detected" + str(stopDetected))
                        print("time need : {}".format(timeNeedOK))
                        if stopDetected and not(timeNeedOK) :  #changer sign width avec index 2 du panneau 
                            toSignDistance = (realSignWidth*focal)/widthStopSign #changer avec liste panneau index 2
                            print("distance :" + str(toSignDistance) + "pixel" + str(widthStopSign))
                            R.speedLock.acquire()
                            speedC= R.wheelSpeed
                            R.speedLock.release()
                            print("vitesse : " + str(speedC))
                            if speedC >= 0.14 :
                                Temps_necessaire = (toSignDistance / speedC)-1  #calcul du temps à  attendre, 1.2 => 100 pour la  vitesse avant -1 pour la reconnaissance
                                print(Temps_necessaire)
                                timeNeedOK = 1
                        
                        # condition du stop pour marquer un arrêt
                       
                        msg = can.Message(arbitration_id=MOT,data=[CMD_V_A, CMD_V_A, 0x00,0,0,0,0,0],extended_id=False)
                        time.sleep(0.01)
                        self.bus.send(msg)
                        #si c'est un panneau stop attendre 5 secondes à l'arrêt
                        if countStop >= Temps_necessaire :
                            countStop = 0
                            timeNeedOK = 0
                            print("OUAIS ON A FINIS")
                            msg = can.Message(arbitration_id=MOT,data=[CMD_V_AS, CMD_V_AS, 0x00,0,0,0,0,0],extended_id=False)
                            time.sleep(0.01)
                            self.bus.send(msg)
                            Temps_necessaire = 9999999999999
                            time.sleep(4)

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
                        countStop = countStop + 0.1
                        
                    elif modeC == "assist" :
                        # comande en fonction des messages de l'ihm
                        msg = can.Message(arbitration_id=MOT,data=[CMD_V, CMD_V, CMD_O,0,0,0,0,0],extended_id=False)
                        time.sleep(0.01)
                        self.bus.send(msg)
                        stopDetected = 0
                        searchDetected = 0
                        timeNeedOK = 0
                    
                    
                else:
                    msg = can.Message(arbitration_id=MOT,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
                    self.bus.send(msg)
                
                time.sleep(0.1)
            msg = can.Message(arbitration_id=MOT,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
            time.sleep(0.01)
            self.bus.send(msg)
            
            
        msg = can.Message(arbitration_id=MOT,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
        time.sleep(0.1)
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
        wheelPerimeter = 0.19 *3.14  
        emergencyOn = 0
        countEmergency = 0
        countSpeed = 0
        wheel_speed = 0
        while self.runEvent.isSet() :
            
            R.lockConnectedDevice.acquire()
            check_connected = R.connectedDevice
            R.lockConnectedDevice.release()
         
            if (check_connected == True):
                
                msg = self.bus.recv()
                """if msg.arbitration_id == MS:
                    Batmes = int(str(msg.data[2:4]).encode('hex'), 16)
                    U = (4095 / Batmes) * (3.3 / 0.2)
                    print(Batmes)"""
                
                if msg.arbitration_id == MS:
                    # Vitesse voiture
                    wheel_speed = int(str(msg.data[6:8]).encode('hex'), 16)
                    R.speedLock.acquire()
                    R.wheelSpeed = (0.01*wheel_speed*wheelPerimeter / 60) #metre/s max : 1.21 m/s donc 4,34 km/H
                    wheel_speed = R.wheelSpeed
                    R.speedLock.release()
                    wheel_speed = round(wheel_speed, 3)
                    #print("speed :" + str(wheel_speed))
                    wheel_angle= int(str(msg.data[0:2]).encode('hex'), 16)
                    #print(wheel_angle)
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
                    distance = int(str(msg.data[0:2]).encode('hex'), 16) 
                    UFL = distance
                    message = "UFL:" + str(distance)+ ";"
                    #print(message)
                    # ultrason avant droit
                    distance = int(str(msg.data[2:4]).encode('hex'), 16)
                    UFR = distance
                    message = "UFR:" + str(distance)+ ";"
                    #print(message)
                    # ultrason avant centre
                    distance = int(str(msg.data[4:6]).encode('hex'), 16)
                    UFC = distance
                    message = "UFC:" + str(distance)+ ";"
                    #print(message)
                

                if UFL<MAX_DISTANCE_US or UFR<MAX_DISTANCE_US or UFC<MAX_DISTANCE_US:
                    self.stopEvent.set()
                    #envoi de message aussi
                    countEmergency = 0
                    if  not(emergencyOn)  :
                        R.constructMsgToIHM("urgent","on")
                        emergencyOn = 1
                else : 
                    if emergencyOn :
                        if countEmergency <10 :
                            countEmergency +=1
                        else:
                            self.stopEvent.clear()
                            countEmergency = 0
                            R.constructMsgToIHM("urgent","off")
                            emergencyOn = 0
            else : 
                emergencyOn = 0
                countEmergency = 0
            time.sleep(0.01)
            countSpeed = countSpeed + 1
            if countSpeed == 100:
                R.constructMsgToIHM("speed",wheel_speed)
                countSpeed = 0
