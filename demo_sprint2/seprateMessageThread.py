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
        listMessagesReceived.acquire()
        ModeLock.acquire()
        JoystickLock.acquire()
        TurboLock.acquire()

        #the message we get is "listMessagesReceived" = "xxxx$xxxxxxx"
        #separate it in two part
        separatedMessage = listMessageReceived.split('$',1)
        key = separatedMessage[0]
        value = separatedMessage[1]

        #there is a table of keys and values
        #Mode, Joystick, Turbo are GLOBAL!!!
        if key == 'mode':
            Mode = value[:] #slice
        elif key == 'joystick':
            Joystick = value[:] #slice
        elif key == 'turbo':
            Turbo = value[:] #slice
        else:
            None

        #Unlock!!!
        TurboLock.release()
        JoystickLock.release()
        ModeLock.release()
        listMessagesReceived.release()

        time.sleep(0.5)


def main():
    seprateMessageThread = SeprateMessageThread()
    seprateMessageThread.start()

    
    q = Queue()

    #Need to use "queue" to send the message????????
    
    #newMessageForQ = [Mode, Joystick, Turbo]
    #for i in range(3):
    #    q.put(newMessageForQ[i])
    
    


if __name__ == '__main__':
    main()
    



