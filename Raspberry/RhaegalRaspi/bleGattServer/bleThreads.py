from utils.serverSettings import *
from utils.service import Application
from threading import Thread
import time
import sharedRessources as r


class BLEServerThread(Thread):
    def __init__(self,runRaspiCodeEvent):
		Thread.__init__(self)
		self.app=Application()
		self.initService()
		#self.initAdvertisement()
		self.setDaemon(True)
		self.runEvent= runRaspiCodeEvent
		print('Init successful server')
	
    def initService(self):
        self.app.add_service(RaspService(0))
        self.app.register()
		
    def initAdvertisement(self):
        adv = RaspAdvertisement(0) #advertize
        adv.register()
		
	def run(self):
		print('server begin to run')
		self.app.run()
		while self.runEvent.isSet() :
		    time.sleep(0.5)
		self.app.quit()
		print('BLE server thread closed')
		
class BLEServer(Application):
    def __init__(self):
		Application.__init__(self)
		self.initService()
		self.initAdvertisement()
	
    def initService(self):
        self.app.add_service(RaspService(0))
        self.app.register()
		
    def initAdvertisement(self):
        adv = RaspAdvertisement(0) #advertize
        adv.register()
	
	def run(self):
        self.mainloop.run()
		#Test launching threads here
		runRaspiCodeEvent = Event()
		runRaspiCodeEvent.set()
		bleTransmitterThread= BLETransmitterThread(bleServerThread,runRaspiCodeEvent)
	def quit(self):
	    print("\nGATT application terminated")
        self.mainloop.quit()
		runRaspiCodeEvent.clear()
		bleTransmitterThread.join()
		
	
		


class BLETransmitterThread(Thread):

    def __init__(self, serverThread,runRaspiCodeEvent):
        Thread.__init__(self)
        self.TXChara = self.retrieveTXCharacteristic(serverThread.app)
        self.setDaemon(True)
        self.runEvent= runRaspiCodeEvent
        print('Open transmitter thread')

    def retrieveTXCharacteristic(self, server):               #get the transmitter characteristic
		serverService=server.services[0]                            #only one service in the app 
		serverCharacteristics = serverService.get_characteristics() #retrieve all characteristics in the service
		return serverCharacteristics[0]                          #the transmitter is the fist one in the list

    def run(self):
        while self.runEvent.isSet() :	
			r.lockConnectedDevice.acquire()
			deviceIsConnected= r.connectedDevice
			r.lockConnectedDevice.release()
			print('test device connection')
			
			if (deviceIsConnected):					
			    r.lockMessagesToSend.acquire()
			    if r.listMessagesToSend:
					print('messages found')
					myMessagesToSend = r.listMessagesToSend
					r.listMessagesToSend = []
			
			    r.lockMessagesToSend.release()
			
			    for i in range(0,len(myMessagesToSend)):
				    self.TXChara.send_tx(myMessagesToSend.pop())
			
			time.sleep(0.5)
        print('Transmitter to server thread closed')
