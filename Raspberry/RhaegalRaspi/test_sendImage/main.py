# -*- coding: utf-8 -*-

from threading import Event
from bleGattServer.bleThreads import BLETransmitterThread, BLEServer
import messageManagement.messageFromIHMManager as msgManager
from testSendImage.sendImage import SendImageThread
import os, sys

def main():      
    runRaspiCodeEvent = Event()
    runRaspiCodeEvent.set()

    #send image
    sendImageThread = SendImageThread(runRaspiCodeEvent)
    
    #BLE part
    bleServer = BLEServer()
    bleTransmitterThread= BLETransmitterThread(bleServer,runRaspiCodeEvent) #for transmitting messages to the server
    
    #message management part
    messageFromIHMThread = msgManager.MessageFromIHMThread(runRaspiCodeEvent)
    
    try:
        bleTransmitterThread.daemon = True
        messageFromIHMThread.daemon = True
        sendImageThread.daemon = True

        bleTransmitterThread.start()
        messageFromIHMThread.start()
        sendImageThread.start()
        bleServer.run() ##################################################################################################### a la fin

    except KeyboardInterrupt:
        print ('Attempting to close all threads')
        runRaspiCodeEvent.clear()
        
        sendImageThread.join()
        bleTransmitterThread.join()
        messageFromIHMThread.join()
    
        print ('All threads successfully closed')
        bleServer.quit()
        os.system("sudo find . -type f -name \"*.pyc\" -delete")
        sys.exit(0)

if __name__ == '__main__':
    main()

