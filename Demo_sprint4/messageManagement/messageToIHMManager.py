# -*- coding: utf-8 -*-
"""
Created on Sat Dec 07 13:27:03 2019

@author: Anaïs, Nicolas
"""
from threading import Thread
import time
import sharedRessources as R

MAX_DISTANCE_US = 20

class BatteryLevelThread(Thread):
    def __init__(self, runEvent):
        Thread.__init__(self)
        self.runEvent= runEvent
        
    def run(self):
        oldBattLvl = "full"
        while self.runEvent.isSet():
            R.lockBatteryLevel.acquire()
            batt = R.batteryLevel
            R.lockBatteryLevel.release()
            
            if(batt<12 and oldBattLvl !="mid"):
                #R.constructMsgToIHM("batt","mid")
                oldBattLvl = "mid"
                
            elif(batt<11 and oldBattLvl !="low"):
                #R.constructMsgToIHM("batt","low")
                oldBattLvl = "low"
            
            elif(batt<11 and oldBattLvl !="critic"):
                #R.constructMsgToIHM("batt","critic")
                oldBattLvl = "critic"           
            
            
            time.sleep(5)
            
class SpeedThread(Thread):
    def __init__(self, runEvent):
        Thread.__init__(self)
        self.runEvent= runEvent
        
    def run(self):
        oldSpeed = 0
        while self.runEvent.isSet():
            R.lockWheelSpeed.acquire()
            speed = R.wheelSpeed
            R.lockWheelSpeed.release()
            
            if(speed or oldSpeed):
                R.constructMsgToIHM("speed",speed)
                oldSpeed = speed           
            
            time.sleep(0.5)
            
            
class EmergencyStopThread(Thread):
    def __init__(self, runEvent):
        Thread.__init__(self)
        self.runEvent= runEvent

    def run(self):
        oldEmergencyStateFront = False
        oldEmergencyStateRear = False
        counterEmergencyStopFront = 0
        counterEmergencyStopRear = 0
        while self.runEvent.isSet():
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
            if((distanceLeftFront<MAX_DISTANCE_US or distanceRightFront<MAX_DISTANCE_US or distanceCenterFront<MAX_DISTANCE_US)and not(oldEmergencyStateFront)):
                R.constructMsgToIHM("urgent","front","on")
                R.lockEmergencyFrontOn.acquire()
                R.emergencyFrontOn = True
                R.lockEmergencyFrontOn.release()
                oldEmergencyStateFront = True
                counterEmergencyStopFront=0
            # emergency stop arrière
            elif((distanceLeftRear<MAX_DISTANCE_US or distanceRightRear<MAX_DISTANCE_US or distanceCenterFront<MAX_DISTANCE_US)and not(oldEmergencyStateRear)):
                R.constructMsgToIHM("urgent","rear","on")
                R.lockEmergencyRearOn.acquire()
                R.emergencyRearOn = True
                R.lockEmergencyRearOn.release()
                oldEmergencyStateRear = True
                counterEmergencyStopRear=0
            #  Emergency stop avant 
            elif(not(distanceLeftFront<MAX_DISTANCE_US or distanceRightFront<MAX_DISTANCE_US or distanceCenterFront<MAX_DISTANCE_US) and oldEmergencyStateFront):
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
            elif(not(distanceLeftRear<MAX_DISTANCE_US or distanceRightRear<MAX_DISTANCE_US or distanceCenterRear<MAX_DISTANCE_US) and oldEmergencyStateRear):
                if(counterEmergencyStopRear<5):
                    counterEmergencyStopRear+=1
                else :
                    R.constructMsgToIHM("urgent","rear","off")
                    R.lockEmergencyRearOn.acquire()
                    R.emergencyRearOn = False
                    R.lockEmergencyRearOn.release()
                    oldEmergencyStateRear = False
                    counterEmergencyStopRear=0
                
            time.sleep(0.1)
            
class SignNotificationThread(Thread):
    def __init__(self, runEvent):
        Thread.__init__(self)
        self.runEvent= runEvent

    def run(self):
        stopSignDetected = False
        searchSignDetected = False
        
        while self.runEvent.isSet():
            #stop sign block
            R.lockWidthStop.acquire()
            stopSignWidth = R.widthStop
            R.lockWidthStop.release()                      
            
            if(stopSignWidth and not(stopSignDetected)):
                R.constructMsgToIHM("sign","stop")
                stopSignDetected = True
            elif(not(stopSignWidth) and (stopSignDetected)):
                stopSignDetected = False
                
            #search sign block
                
            R.lockWidthSearch.acquire()
            searchSignWidth = R.widthSearch
            R.lockWidthSearch.release()
            
            if(searchSignWidth and not(searchSignDetected)):
                R.constructMsgToIHM("sign","search")
                searchSignDetected = True
            elif(not(searchSignWidth) and (searchSignDetected)):
                searchSignDetected = False
            
            
            time.sleep(0.1)
            
        
        
    
        
