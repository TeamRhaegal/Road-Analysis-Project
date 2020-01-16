#!/usr/bin/env python
# coding=utf-8

import sys, os
import glob


input_path = "/home/vincent/Documents/Travail/dummywork/temp/"
output_path = "/home/vincent/Documents/Travail/dummywork/stupid/"

image_counter = 794

FOLDERNAME = input_path
IMAGE_FOLDER = glob.glob(FOLDERNAME+"*.jpg")

for image in IMAGE_FOLDER:
    os.rename(image, os.path.join(output_path,str(image_counter)+'.jpg'))
    image_counter = image_counter +1

