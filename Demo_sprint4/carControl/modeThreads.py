# -*- coding: utf-8 -*-
"""
Created on Sat Dec 07 11:28:11 2019

@author: Anaïs, Nicolas
"""
import time
import can
from threading import Thread, Lock
import sharedRessources as R


MOT=0x010     #identifiant commande moteur CAN
CMD_STOP = 0x00
CMD_V_BACK = 35 + 0x80
CMD_V_MIN = 50
CMD_V_SLOW = 65 + 0x80
CMD_V_TURBO = 75 + 0x80
CMD_O_LEFT = 0x80
CMD_O_RIGHT = 100 + 0x80
CMD_O_MIN = 50


#for auto only
REAL_SIGN_WIDTH = 0.20  #nb à déterminer en cm
FOCAL = 342

#thread emergency+modeThread
"""
emergencyOn = False
lockEmergencyOn = Lock()
"""
class ModeThread(Thread):
    def __init__(self, bus,intModeL):
        Thread.__init__(self)
        self.bus = bus
        self.intModeL = intModeL
    
    def sendMesgToMot(self,cmdV,cmdO):
        msg = can.Message(arbitration_id=MOT,data=[cmdV, cmdV, cmdO,0,0,0,0,0],extended_id=False)
        time.sleep(0.01)
        self.bus.send(msg)
        
        

class ModeAutoThread (ModeThread):
    def __init__(self, bus):
        ModeThread.__init__(self,bus,2)
        
    def run(self):
        self.sendMesgToMot(CMD_V_SLOW,CMD_STOP)     
        currentModeL=self.intModeL
        counterStopOn = False
        finalValueStopCounter = 0
        counterStop=0
        
        while (currentModeL==self.intModeL):
            # Emergency stop block
            R.lockEmergencyOn.acquire()
            stateEmergency = R.emergencyOn
            R.lockEmergencyOn.release()
            
            if(stateEmergency):
                R.modeLock.acquire()
                mode = "assist"
                R.modeLock.release()
                
            # Stop sign block
            
            if(counterStopOn):
                if(counterStop<finalValueStopCounter):
                    counterStop+=0.1
                else:
                    self.sendMesgToMot(CMD_STOP,CMD_STOP)   
                    time.sleep(4)
                    self.sendMesgToMot(CMD_V_SLOW,CMD_STOP) 
                    counterStop=0
                    finalValueStopCounter=0
                    counterStopOn = False
            
            else:    
                R.lockWidthStop.acquire()                 
                widthStopSign = R.widthStop           
                R.lockWidthStop.release()
                if(widthStopSign):
                    toSignDistance = (REAL_SIGN_WIDTH*FOCAL)/widthStopSign
                    R.lockWheelSpeed.acquire()
                    speedC= R.wheelSpeed
                    R.lockWheelSpeed.release()
                    if speedC >= 0.14 :
                        finalValueStopCounter = (toSignDistance / speedC)-3  #calcul du temps à  attendre, 1.2 => 100 pour la  vitesse avant -1 pour la reconnaissance
                        counterStopOn=True
                    
            
            R.lockModeLaunched.acquire()
            currentModeL = R.modeLaunched
            R.lockModeLaunched.release()
            time.sleep(0.1)
        
        self.sendMesgToMot(CMD_STOP,CMD_STOP) 
        
class ModeAssistThread (ModeThread):
    def __init__(self, bus):
        ModeThread.__init__(self,bus,1)
        
    def run(self):
        self.sendMesgToMot(CMD_STOP,CMD_STOP)     
        currentModeL=self.intModeL
        cmdV = CMD_STOP
        cmdO = CMD_STOP
        R.turboLock.acquire()
        R.turbo ="off"
        R.turboLock.release()
        R.joystickLock.acquire()
        R.joystick = "none"
        R.joystickLock.release()
        R.stateLock.acquire()
        R.state = "off"
        R.stateLock.release()
        
        while (currentModeL==self.intModeL):
            R.stateLock.acquire()                 
            currentState = R.state         
            R.stateLock.release()
            if(currentState=="on"):
                R.joystickLock.acquire()                 
                currentJoystick = R.joystick         
                R.joystickLock.release()
                if(currentJoystick =="none"):
                    cmdO = CMD_O_MIN
                    cmdV = CMD_V_MIN 

                elif(currentJoystick=="right"):
                    cmdO = CMD_O_RIGHT
                    cmdV= CMD_V_MIN 

                elif(currentJoystick=="left"):
                    cmdO = CMD_O_LEFT
                    cmdV = CMD_V_MIN 

                elif(currentJoystick=="front"):
                    R.turboLock.acquire()                 
                    currentTurbo = R.turbo        
                    R.turboLock.release()

                    if(currentTurbo=="on"):
                        cmdV=CMD_V_TURBO
                    else:
                        cmdV= CMD_V_SLOW

                    cmdO = CMD_O_MIN                    
                         
                elif(currentJoystick=="front&right"):
                    cmdO = CMD_O_RIGHT
                    cmdV= CMD_V_SLOW

                elif(currentJoystick=="front&left"):
                    cmdO = CMD_O_LEFT
                    cmdV= CMD_V_SLOW
                 
                elif(currentJoystick=="back"):
                    cmdO = CMD_O_MIN
                    cmdV= CMD_V_BACK
                 
                elif(currentJoystick=="back&right"):
                    cmdO = CMD_O_RIGHT
                    cmdV= CMD_V_BACK
                 
                elif(currentJoystick=="back&left"):
                    cmdO = CMD_O_LEFT
                    cmdV= CMD_V_BACK

                self.sendMesgToMot(cmdV,cmdO)
                         
                         
            else:
                 self.sendMesgToMot(CMD_STOP,CMD_STOP)
                    
            
            R.lockModeLaunched.acquire()
            currentModeL = R.modeLaunched
            R.lockModeLaunched.release()
            time.sleep(0.1)
        
        self.sendMesgToMot(CMD_STOP,CMD_STOP) 
