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
                if(len(separatedMessage)==2):
					key = separatedMessage[0]
					value = separatedMessage[1]

					#there is a table of keys and values
					#Mode, Joystick, Turbo are GLOBAL!!!
					if key == 'mode':
						sr.lockMode.acquire()
						sr.mode = value #slice
						sr.lockMode.release()
					elif key == 'joy':
						sr.lockJoystick.acquire()
						sr.joystick = value #slice
						sr.lockJoystick.release()
					elif key == 'turbo':
						sr.lockTurbo.acquire()
						sr.turbo = value #slice
						sr.lockTurbo.release()
					elif key == 'state':
						sr.lockState.acquire()
						sr.state = value 
						sr.lockState.release()
					elif key == 'connect':
						sr.lockConnectedDevice.acquire()
						if value == 'on':
							sr.connectedDevice = True
						else:
							sr.connectedDevice = False
							sr.lockMode.acquire()
							sr.mode = "assist" #slice
							sr.lockMode.release()
							sr.lockJoystick.acquire()
							sr.joystick = "none" #slice
							sr.lockJoystick.release()
							sr.lockTurbo.acquire()
							sr.turbo = "off" #slice
							sr.lockTurbo.release()
						
							
						sr.lockConnectedDevice.release()
					else:
						None

            time.sleep(0.1)



    



