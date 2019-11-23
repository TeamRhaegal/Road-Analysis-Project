from queue import Queue
import sharedRessources as sr
from threading import Thread
from threading import Lock
from time import time

#Need to "import" a document for the "listMessagesReceived" etc.

#creat a threading
class SeprateMessageThread(Thread):
    def __init__(self, runEvent):
        self.runEvent = runEvent
    def run(self):
        while runEvent.isSet():
        #Lock!!!
            sr.lockMessagesReceived.acquire()

            sr.modeLock.acquire()
            sr.joystickLock.acquire()
            sr.turboLock.acquire()
            sr.lockConnectedDevice.acquire()

            #the message we get is "listMessagesReceived" = "xxxx$xxxxxxx"
            #separate it in two part

            for i in range(0,len(sr.listMessageReceived)):

                separatedMessage = sr.listMessageReceived[i].split('$',1)
                key = separatedMessage[0]
                value = separatedMessage[1]

                #there is a table of keys and values
                #Mode, Joystick, Turbo are GLOBAL!!!
                if key == 'mode':
                    sr.mode = value[:] #slice
                elif key == 'joystick':
                    sr.joystick = value[:] #slice
                elif key == 'turbo':
                    sr.turbo = value[:] #slice
                elif key == 'connectedDevice':
                    connectedDevice_c = value[:]
                    if connectedDevice_c = 'on':
                        sr.connectedDevice = True
                    else:
                        sr.connectedDevice = Flase
                else:
                    None

            #Unlock!!!
            sr.lockConnectedDevice.release()
            sr.turboLock.release()
            sr.joystickLock.release()
            sr.modeLock.release()
            sr.lockMessagesReceived.release()

            time.sleep(0.5)



    



