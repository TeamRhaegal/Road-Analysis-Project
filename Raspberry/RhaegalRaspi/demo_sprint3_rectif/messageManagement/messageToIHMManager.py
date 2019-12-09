# -*- coding: utf-8 -*-
"""
Created on Sat Dec 07 13:27:03 2019

@author: Anaïs, Nicolas
"""
from threading import Thread
import time
import sharedRessources as R

MAX_DISTANCE_US = 30

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
                R.constructMsgToIHM("batt","mid")
                oldBattLvl = "mid"
                
            elif(batt<11 and oldBattLvl !="low"):
                R.constructMsgToIHM("batt","low")
                oldBattLvl = "low"
            
            elif(batt<11 and oldBattLvl !="critic"):
                R.constructMsgToIHM("batt","critic")
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
        oldEmergencyState = False
        counterEmergencyStop = 0
        while self.runEvent.isSet():
            R.lockFrontRadar.acquire()
            distanceLeft = R.UFL 
            distanceRight = R.UFR 
            distanceCenter = R.UFC 
            R.lockFrontRadar.release()
            
            if((distanceLeft<MAX_DISTANCE_US or distanceRight<MAX_DISTANCE_US or distanceCenter<MAX_DISTANCE_US)and not(oldEmergencyState)):
                R.constructMsgToIHM("urgent","on")
                R.lockEmergencyOn.acquire()
                R.emergencyOn = True
                R.lockEmergencyOn.release()
                oldEmergencyState = True
                counterEmergencyStop=0
            elif(not(distanceLeft<MAX_DISTANCE_US or distanceRight<MAX_DISTANCE_US or distanceCenter<MAX_DISTANCE_US) and oldEmergencyState):
                if(counterEmergencyStop<5):
                    counterEmergencyStop+=1
                else :
                    R.constructMsgToIHM("urgent","off")
                    R.lockEmergencyOn.acquire()
                    R.emergencyOn = False
                    R.lockEmergencyOn.release()
                    oldEmergencyState = False
                    counterEmergencyStop=0
                
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
            
        
        
    
        
