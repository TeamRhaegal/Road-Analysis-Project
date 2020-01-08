# -*- coding: utf-8 -*-
#!/usr/bin/env python
import cv2


IMAGE_PATH = "/home/pi/Documents/projet_SIEC/Road-Analysis-Project/Raspberry/RhaegalRaspi/test_sendImage/266.jpg"

if __name__ == "__main__":
	shared_image = cv2.imread(IMAGE_PATH)
	#shared_image = cv2.cvtColor(shared_image, cv2.COLOR_BGR2RGB)
	pass
