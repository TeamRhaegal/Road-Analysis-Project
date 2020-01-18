# -*- coding: utf-8 -*-
"""
Created on Sat Dec 07 13:27:03 2019

@author: Anaïs, Nicolas
"""
from threading import Thread
import time
import sharedRessources as R

MAX_DISTANCE_FRONT = 35  #FRONT maximum distance in cm when an obstacle is considered as a danger
MAX_DISTANCE_BACK = 45 #BACK maximum distance in cm when an obstacle is considered as a danger
           
class SpeedThread(Thread):
    def __init__(self, runEvent):
        Thread.__init__(self)
        self.runEvent= runEvent
        self.setDaemon(True)
        
    def run(self):
        oldSpeed = 0
        while self.runEvent.isSet():
            R.lockConnectedDevice.acquire()
            check_connected = R.connectedDevice
            R.lockConnectedDevice.release()
            if(check_connected):
                R.lockWheelSpeed.acquire()
                speed = R.wheelSpeed
                R.lockWheelSpeed.release()
                
                if(speed or oldSpeed):
                    R.constructMsgToIHM("speed",speed)
                    oldSpeed = speed  
            else:
                oldSpeed = 0            
            time.sleep(0.5)
            
            
class EmergencyStopThread(Thread):
    def __init__(self, runEvent):
        Thread.__init__(self)
        self.runEvent= runEvent
        self.setDaemon(True)

    def run(self):
        oldEmergencyStateFront = False
        oldEmergencyStateRear = False
        counterEmergencyStopFront = 0
        counterEmergencyStopRear = 0
        while self.runEvent.isSet():
            R.lockConnectedDevice.acquire()
            check_connected = R.connectedDevice
            R.lockConnectedDevice.release()
            if(check_connected):
                #retrieving sensors information from global variables
                R.lockFrontRadar.acquire()
                distanceLeftFront = R.UFL 
                distanceRightFront = R.UFR 
                distanceCenterFront = R.UFC 
                R.lockFrontRadar.release()
                
                R.lockRearRadar.acquire()
                distanceLeftRear = R.URL 
                distanceRightRear = R.URR 
                distanceCenterRear = R.URC
                R.lockRearRadar.release()
                #emergency stop avant
                if((distanceLeftFront<MAX_DISTANCE_FRONT or distanceRightFront<MAX_DISTANCE_FRONT or distanceCenterFront<MAX_DISTANCE_FRONT)and not(oldEmergencyStateFront)):
                    R.constructMsgToIHM("urgent","front","on")
                    R.lockEmergencyFrontOn.acquire()
                    R.emergencyFrontOn = True
                    R.lockEmergencyFrontOn.release()
                    oldEmergencyStateFront = True
                    counterEmergencyStopFront=0
                # emergency stop arrière
                elif((distanceLeftRear<MAX_DISTANCE_BACK or distanceRightRear<MAX_DISTANCE_BACK or distanceCenterRear<MAX_DISTANCE_BACK)and not(oldEmergencyStateRear)):
                    R.constructMsgToIHM("urgent","rear","on")
                    R.lockEmergencyRearOn.acquire()
                    R.emergencyRearOn = True
                    R.lockEmergencyRearOn.release()
                    oldEmergencyStateRear = True
                    counterEmergencyStopRear=0
                #  Emergency stop avant 
                elif(not(distanceLeftFront<MAX_DISTANCE_FRONT or distanceRightFront<MAX_DISTANCE_FRONT or distanceCenterFront<MAX_DISTANCE_FRONT) and oldEmergencyStateFront):
                    if(counterEmergencyStopFront<5):
                        counterEmergencyStopFront+=1
                    else :
                        R.constructMsgToIHM("urgent","front","off")
                        R.lockEmergencyFrontOn.acquire()
                        R.emergencyFrontOn = False
                        R.lockEmergencyFrontOn.release()
                        oldEmergencyStateFront = False
                        counterEmergencyStopFront=0
                #emergency stop  arrière
                elif(not(distanceLeftRear<MAX_DISTANCE_BACK or distanceRightRear<MAX_DISTANCE_BACK or distanceCenterRear<MAX_DISTANCE_BACK) and oldEmergencyStateRear):
                    if(counterEmergencyStopRear<5):
                        counterEmergencyStopRear+=1
                    else :
                        R.constructMsgToIHM("urgent","rear","off")
                        R.lockEmergencyRearOn.acquire()
                        R.emergencyRearOn = False
                        R.lockEmergencyRearOn.release()
                        oldEmergencyStateRear = False
                        counterEmergencyStopRear=0
            else:
                oldEmergencyStateFront = False
                oldEmergencyStateRear = False
                counterEmergencyStopFront = 0
                counterEmergencyStopRear = 0
                
            time.sleep(0.1)
            
class SignNotificationThread(Thread):
    def __init__(self, runEvent):
        Thread.__init__(self)
        self.runEvent= runEvent
        self.setDaemon(True)

    def run(self):
        stopSignDetected = False
        searchSignDetected = False
        
        while self.runEvent.isSet():
            R.lockConnectedDevice.acquire()
            check_connected = R.connectedDevice
            R.lockConnectedDevice.release()
            if(check_connected):
                #stop sign block
                R.lockWidthStop.acquire()
                stopSignWidth = R.widthStop
                R.lockWidthStop.release()                      
                
                if(stopSignWidth and not(stopSignDetected)):
                    R.constructMsgToIHM("sign","stop","on")
                    stopSignDetected = True
                elif(not(stopSignWidth) and (stopSignDetected)):
                    R.constructMsgToIHM("sign","stop","off")
                    stopSignDetected = False
                    
                #search sign block
                    
                R.lockWidthSearch.acquire()
                searchSignWidth = R.widthSearch
                R.lockWidthSearch.release()
                
                if(searchSignWidth and not(searchSignDetected)):
                    R.constructMsgToIHM("sign","search","on")
                    searchSignDetected = True
                elif(not(searchSignWidth) and (searchSignDetected)):
                    R.constructMsgToIHM("sign","search","off")
                    searchSignDetected = False
            
            else:
                 stopSignDetected = False
                 searchSignDetected = False
            
            time.sleep(0.1)
			
class SearchObjectNotificationThread(Thread):
    def __init__(self, runEvent):
        Thread.__init__(self)
        self.runEvent= runEvent
        self.setDaemon(True)
		
    def run(self):
        smallObjectDetected = False
        mediumObjectDetected = False
        bigObjectDetected = False
        
        while self.runEvent.isSet():
            R.lockConnectedDevice.acquire()
            check_connected = R.connectedDevice
            R.lockConnectedDevice.release()
            if(check_connected):
                # small object block
                R.lockWidthSmall.acquire()
                smallObjectWidth = R.widthSmall
                R.lockWidthSmall.release()                      
                
                if(smallObjectWidth and not(smallObjectDetected)):
                    R.constructMsgToIHM("object","small")
                    smallObjectDetected = True
                elif(not(smallObjectWidth) and (smallObjectDetected)):
                    smallObjectDetected = False
                    
                # medium object block
                R.lockWidthMedium.acquire()
                mediumObjectWidth = R.widthMedium
                R.lockWidthMedium.release()  
                
                if(mediumObjectWidth and not(mediumObjectDetected)):
                    R.constructMsgToIHM("object","medium")
                    mediumObjectDetected = True
                elif(not(mediumObjectWidth) and (mediumObjectDetected)):
                    mediumObjectDetected = False
                    
                # big object block
                R.lockWidthBig.acquire()
                bigObjectWidth = R.widthBig
                R.lockWidthBig.release()  
                
                if(bigObjectWidth and not(bigObjectDetected)):
                    R.constructMsgToIHM("object","big")
                    bigObjectDetected = True
                elif(not(bigObjectWidth) and (bigObjectDetected)):
                    bigObjectDetected = False
                    
            else:
                smallObjectDetected = False
                mediumObjectDetected = False
                bigObjectDetected = False
                
            time.sleep(0.1)     
    
        
