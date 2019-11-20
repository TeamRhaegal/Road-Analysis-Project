from utils.serverSettings import *
from utils.service import Application
from threading import Thread
from time import time
import sharedRessources

class BLEServer(Application):
    def __init__(self):
		Application.__init__(self)
		self.initService()
		self.initAdvertisement()
	
    def initService(self):
        self.add_service(RaspService(0))
        self.register()
		
    def initAdvertisement(self):
        adv = RaspAdvertisement(0) #advertize
        adv.register()


class BLETransmitterThread(Thread):

    def __init__(self, server):
        Thread.__init__(self)
        self.TXChara = self.retrieveTXCharacteristic(server)

    def retrieveTXCharacteristic(self, server):               #get the transmitter characteristic
		serverService=server.services[0]                            #only one service in the app 
		serverCharacteristics = serverService.get_characteristics() #retrieve all characteristics in the service
		return serverCharacteristics[0]                          #the transmitter is the fist one in the list

    def run(self):
        while True :
			global mutexMessagesToSend
			global listMessagesToSend
			
			mutexMessagesToSend.lock()
			if listMessagesToSend:
				myMessagesToSend = listMessagesToSend
				listMessagesToSend.clear()
			mutexMessagesToSend.unlock()
			
			for i in range(0,len(listMessagesToSend)):
				TXChara.send_tx(listMessagesToSend.popleft())
			
			time.sleep(0.5)
