# -*- coding: utf-8 -*-
"""
Created on Sat Dec 07 09:26:29 2019

@author: Anaïs, Nicolas
"""

import can
import time
import os
from threading import Thread, Event
import sharedRessources as R
from modeThreads import ModeAutoThread, ModeAssistThread


#Receiver

WHEEL_PERIMETER = 0.19 *3.14  

US2=0x001      #identifiant Ultrasons arrière CAN
US1=0x000      ##identifiant Ultrasons arrière CAN
MS=0x100       #id for battery+speed

class CanControllerThread(Thread):
    def __init__(self, runEvent):
        Thread.__init__(self)
        self.bus = self.getBus() #initialization of CAN bus
        self.runEvent= runEvent
        self.connectEvent = Event()  
        self.modeControlThread = ModeControlThread(self.bus,self.connectEvent) 
        self.canReceiverThread = CanReceiverThread(self.bus,self.connectEvent)
        
    def getBus(self):
        os.system("sudo /sbin/ip link set can0 up type can bitrate 400000")
        try:
            return can.interface.Bus(channel='can0', bustype='socketcan_native')
        except OSError:
            print('Cannot find PiCAN board.')
            
    def run(self):
        while self.runEvent.isSet():
            R.lockConnectedDevice.acquire()
            check_connected = R.connectedDevice
            R.lockConnectedDevice.release()
            
            if(check_connected and not(self.connectEvent.isSet())):
                self.connectEvent.set();
                self.modeControlThread = ModeControlThread(self.bus,self.connectEvent)             
                self.canReceiverThread = CanReceiverThread(self.bus,self.connectEvent)
                
                self.modeControlThread.start()
                self.canReceiverThread.start()
                
            elif(not(check_connected) and (self.connectEvent.isSet())):
                self.connectEvent.clear()
                self.modeControlThread.join()
                self.canReceiverThread.join()
                
            time.sleep(0.3)
        
        if (self.connectEvent.isSet()):
            self.connectEvent.clear()
            self.canTransmitterThread.join()
            self.canReceiverThread.join()
                

class ModeControlThread(Thread):
    def __init__(self, bus, connectEvent):
        Thread.__init__(self)
        self.bus = bus
        self.connectEvent= connectEvent
        self.modeAutoThread = ModeAutoThread(self.bus)
        self.modeAssistThread = ModeAssistThread(self.bus)
    
    def run(self):
        while self.connectEvent.isSet():                             
            R.lockMode.acquire()
            modeC = R.mode
            R.lockMode.release()
            
            R.lockModeLaunched.acquire()
            currentModeLaunched = R.modeLaunched
            R.lockModeLaunched.release()
            
            if (modeC=="auto" and currentModeLaunched!=2):
                R.lockModeLaunched.acquire()
                R.modeLaunched = 2
                R.lockModeLaunched.release()
                if (currentModeLaunched==1):
                    self.modeAssistThread.join() 
                
                self.modeAutoThread = ModeAutoThread(self.bus)
                self.modeAutoThread.start()
                
            if(modeC=="assist" and currentModeLaunched!=1):
                R.lockModeLaunched.acquire()
                R.modeLaunched = 1
                R.lockModeLaunched.release()
                if (currentModeLaunched==2):
                    self.modeAutoThread.join() 
                
                self.modeAssistThread = ModeAssistThread(self.bus)
                self.modeAssistThread.start()
                
            time.sleep(0.1)
            
        R.lockModeLaunched.acquire()
        currentModeLaunched = R.modeLaunched
        R.modeLaunched=0
        R.lockModeLaunched.release()
        
        if(currentModeLaunched==1):
            self.modeAssistThread.join()
        elif(currentModeLaunched==2):
            self.modeAutoThread.join()
            
            
'''
This thread receive all the sensors informations from the can bus and update 
global variables associated to this sensors
'''            
            
class CanReceiverThread(Thread):
    def __init__(self, bus, connectEvent):
        Thread.__init__(self)
        self.bus = bus
        self.connectEvent= connectEvent
        
    def run(self):
        while self.connectEvent.isSet():    
            msg = self.bus.recv()
            
            if msg.arbitration_id == MS:
                wheel_speed = int(str(msg.data[6:8]).encode('hex'), 16)
                batt = int(str(msg.data[2:4]).encode('hex'), 16)
                
                R.lockWheelSpeed.acquire()
                R.wheelSpeed = (0.01*wheel_speed*WHEEL_PERIMETER / 60)  #computing speed in m/s
                R.lockWheelSpeed.release()
                
                R.lockBatteryLevel.acquire()
                R.batteryLevel = (4095 / batt) * (3.3 / 0.2)
                R.lockBatteryLevel.release()
                
            if msg.arbitration_id == US1: #front radar
                
                R.lockFrontRadar.acquire()
                R.UFL = int(str(msg.data[0:2]).encode('hex'), 16) #left side
                R.UFR = int(str(msg.data[2:4]).encode('hex'), 16) #right side
                R.UFC = int(str(msg.data[4:6]).encode('hex'), 16) #center
                R.lockFrontRadar.release()
                
            if msg.arbitration_id == US2: #rear radar
                
                R.lockRearRadar.acquire()
                R.URL = int(str(msg.data[0:2]).encode('hex'), 16) #left side
                R.URR = int(str(msg.data[2:4]).encode('hex'), 16) #right side
                R.URC = int(str(msg.data[4:6]).encode('hex'), 16) #center
                R.lockRearRadar.release()
            
            time.sleep(0.01)
                        
            
    
    
        
        
