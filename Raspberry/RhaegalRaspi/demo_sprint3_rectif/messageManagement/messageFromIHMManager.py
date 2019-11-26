from queue import Queue
import sharedRessources as sr
from threading import Thread
from threading import Lock
import time

#Need to "import" a document for the "listMessagesReceived" etc.

#creat a threading
class MessageFromIHMThread(Thread):
    def __init__(self, runEvent):
        Thread.__init__(self)
        self.runEvent = runEvent
    def run(self):
        while self.runEvent.isSet():
        #Lock!!!
            sr.lockMessagesReceived.acquire()
            listMsg = sr.listMessagesReceived
            sr.listMessagesReceived= [] 
            sr.lockMessagesReceived.release()

            #the message we get is "listMessagesReceived" = "xxxx$xxxxxxx"
            #separate it in two part

            for i in range(0,len(listMsg)):

                separatedMessage = listMsg[i].split('$',1)
                key = separatedMessage[0]
                value = separatedMessage[1]
      

                #there is a table of keys and values
                #Mode, Joystick, Turbo are GLOBAL!!!
                if key == 'mode':
                    sr.modeLock.acquire()
                    sr.mode = value #slice
                    sr.modeLock.release()
                elif key == 'joy':
                    sr.joystickLock.acquire()
                    sr.joystick = value #slice
                    sr.joystickLock.release()
                elif key == 'turbo':
                    sr.turboLock.acquire()
                    sr.turbo = value #slice
                    sr.turboLock.release()
                elif key == 'state':
                    sr.stateLock.acquire()
                    sr.state = value 
                    sr.stateLock.release()
                elif key == 'connect':
                    sr.lockConnectedDevice.acquire()
                    if value == 'on':
                        sr.connectedDevice = True
                    else:
                        sr.connectedDevice = False
                        sr.modeLock.acquire()
                        sr.mode = "assist" #slice
                        sr.modeLock.release()
                        sr.joystickLock.acquire()
                        sr.joystick = "none" #slice
                        sr.joystickLock.release()
                        sr.turboLock.acquire()
                        sr.turbo = "off" #slice
                        sr.turboLock.release()
                    
                        
                    sr.lockConnectedDevice.release()
                else:
                    None

            time.sleep(0.1)



    



