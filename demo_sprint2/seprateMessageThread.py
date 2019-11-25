from queue import Queue
import sharedRessources as sr
from threading import Thread
from threading import Lock
import time

#Need to "import" a document for the "listMessagesReceived" etc.

#creat a threading
class SeprateMessageThread(Thread):
    def __init__(self, runEvent):
        Thread.__init__(self)
        self.runEvent = runEvent
    def run(self):
        while self.runEvent.isSet():
        #Lock!!!
            sr.lockMessagesReceived.acquire()

            sr.modeLock.acquire()
            sr.joystickLock.acquire()
            sr.turboLock.acquire()
            sr.lockConnectedDevice.acquire()

            #the message we get is "listMessagesReceived" = "xxxx$xxxxxxx"
            #separate it in two part

            for i in range(0,len(sr.listMessagesReceived)):

                separatedMessage = sr.listMessagesReceived[i].split('$',1)
                key = separatedMessage[0]
                value = separatedMessage[1]
      

                #there is a table of keys and values
                #Mode, Joystick, Turbo are GLOBAL!!!
                if key == 'mode':
                    sr.mode = value #slice
                elif key == 'joy':
                    sr.joystick = value #slice
                elif key == 'turbo':
                    sr.turbo = value #slice
                elif key == 'connect':
                    if value == 'on':
                        sr.connectedDevice = True
                    else:
                        sr.connectedDevice = False
                    print(sr.connectedDevice)
                else:
                    None

            #Unlock!!!
            sr.listMessagesReceived= [] 
            sr.lockConnectedDevice.release()
            sr.turboLock.release()
            sr.joystickLock.release()
            sr.modeLock.release()
            sr.lockMessagesReceived.release()

            time.sleep(0.1)



    



