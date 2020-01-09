# -*- coding: utf-8 -*-

import sys, os, traceback
from threading import Thread
import time

class Debug(Thread):
	
	def __init__(self, runEvent):
		Thread.__init__(self)
		self.runEvent = runEvent
		self.setDaemon(True)
		pass

	def run(self):
		while(self.runEvent.isSet()):

			time.sleep(2)
			print(traceback.print_exc())
			pass
