from queue import Queue
#from mutex import Mutex #not fonction in Pyhton3
from threading import Thread
from threading import Lock
from time import time

#Need to "import" a document for the "listMessagesReceived" etc.

#creat a threading
class SeprateMessageThread(Thread):
    def run(self):
        #Lock!!!
        lockMessagesReceived.acquire()
        
        modeLock.acquire()
        joystickLock.acquire()
        turboLock.acquire()

        #the message we get is "listMessagesReceived" = "xxxx$xxxxxxx"
        #separate it in two part
        
        for i in range(0,len(listMessageReceived)):
            
            separatedMessage = listMessageReceived[i].split('$',1)
            key = separatedMessage[0]
            value = separatedMessage[1]

            #there is a table of keys and values
            #Mode, Joystick, Turbo are GLOBAL!!!
            if key == 'mode':
                mode = value[:] #slice
            elif key == 'joystick':
                joystick = value[:] #slice
            elif key == 'turbo':
                turbo = value[:] #slice
            else:
                None

        #Unlock!!!
        turboLock.release()
        joystickLock.release()
        modeLock.release()
        lockMessagesReceived.release()

        time.sleep(0.5)


def main():
    seprateMessageThread = SeprateMessageThread()
    seprateMessageThread.start()

    
    #q = Queue()

    #Need to use "queue" to send the message????????
    
    #newMessageForQ = [Mode, Joystick, Turbo]
    #for i in range(3):
    #    q.put(newMessageForQ[i])
    
    


if __name__ == '__main__':
    main()
    



