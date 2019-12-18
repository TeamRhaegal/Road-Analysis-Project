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
CMD_STOP = 0x00     # command to stop the motor
CMD_V_BACK = 35 + 0x80 # command to go backward 
CMD_V_MIN = 50      
CMD_V_SLOW = 65 + 0x80 # command to go forward at a small speed
CMD_V_TURBO = 75 + 0x80 # command to go forward at a high speed
CMD_O_LEFT = 0x80  # command to turn the wheel to left
CMD_O_RIGHT = 100 + 0x80  # command to turn the wheel to right
CMD_O_MIN = 50


#for auto only
REAL_SIGN_WIDTH = 0.20  #real size of the sign in cm
FOCAL = 342   # computed focal of the raspicam

#thread emergency+modeThread
"""
emergencyOn = False
lockEmergencyOn = Lock()
"""

"""
The class mode is the mother class of Mode auto and Mode assist : 
    attributes : mode, CAN bus
    methods : sending message to the CAN bus
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
            R.lockEmergencyFrontOn.acquire()
            stateEmergencyFront = R.emergencyFrontOn
            R.lockEmergencyFrontOn.release()
            
            
            if(stateEmergencyFront):  #testing if an emergency stop is needed in front of the car, => switch in assist mode and stop the vehicle
                R.modeLock.acquire()
                R.mode = "assist"
                R.modeLock.release()
                
            # Stop sign block
            
            if(counterStopOn):                 
                if(counterStop<finalValueStopCounter): # counting until we reach the computed time to wait until reaching the "stop" sign
                    counterStop+=0.1
                else:
                    # reaction to the stop sign : the car stop during 4 seconds and go forward again
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
                    toSignDistance = (REAL_SIGN_WIDTH*FOCAL)/widthStopSign  #computing the distance to the sign detected using the width in pixel of the sign
                    R.lockWheelSpeed.acquire()
                    speedC= R.wheelSpeed
                    R.lockWheelSpeed.release()
                    if speedC >= 0.14 :
                        finalValueStopCounter = (toSignDistance / speedC)-3  #computing time to wait until the car reachs ths "stop" sign
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
       #initialisation of all variables
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
        emergencyFront = False
        emergencyRear = False
        
        while (currentModeL==self.intModeL):
            R.stateLock.acquire()                 
            currentState = R.state         
            R.stateLock.release()
            if(currentState=="on"):
                R.joystickLock.acquire()                 
                currentJoystick = R.joystick     #joystick    
                R.joystickLock.release()
                
                R.lockEmergencyFrontOn.acquire()
                emergencyFront = R.emergencyFrontOn     #front emergency
                R.lockEmergencyFrontOn.release()
                
                R.lockEmergencyRearOn.acquire()
                emergencyRear = R.emergencyRearOn       # rear emergency 
                R.lockEmergencyRearOn.release()
                
                # sending the correct command according to the HMI messages
                if(currentJoystick =="none"):
                    cmdO = CMD_O_MIN
                    cmdV = CMD_V_MIN 

                elif(currentJoystick=="right"):
                    cmdO = CMD_O_RIGHT
                    cmdV= CMD_V_MIN 

                elif(currentJoystick=="left"):
                    cmdO = CMD_O_LEFT
                    cmdV = CMD_V_MIN 

                elif(currentJoystick=="front" and not(emergencyFront)):
                    R.turboLock.acquire()                 
                    currentTurbo = R.turbo        
                    R.turboLock.release()

                    if(currentTurbo=="on"):
                        cmdV=CMD_V_TURBO
                    else:
                        cmdV= CMD_V_SLOW

                    cmdO = CMD_O_MIN                    
                         
                elif(currentJoystick=="front&right" and not(emergencyFront)):
                    cmdO = CMD_O_RIGHT
                    cmdV= CMD_V_SLOW

                elif(currentJoystick=="front&left" and not(emergencyFront)):
                    cmdO = CMD_O_LEFT
                    cmdV= CMD_V_SLOW
                 
                elif(currentJoystick=="back" and not(emergencyRear)):
                    cmdO = CMD_O_MIN
                    cmdV= CMD_V_BACK
                 
                elif(currentJoystick=="back&right" and not(emergencyRear)):
                    cmdO = CMD_O_RIGHT
                    cmdV= CMD_V_BACK
                 
                elif(currentJoystick=="back&left" and not(emergencyRear)):
                    cmdO = CMD_O_LEFT
                    cmdV= CMD_V_BACK

                self.sendMesgToMot(cmdV,cmdO) #sending command to the motors
                         
                         
            else:
                 self.sendMesgToMot(CMD_STOP,CMD_STOP)    #sending command to the motors
                    
            
            R.lockModeLaunched.acquire()
            currentModeL = R.modeLaunched
            R.lockModeLaunched.release()
            time.sleep(0.1)
        
        self.sendMesgToMot(CMD_STOP,CMD_STOP) 
