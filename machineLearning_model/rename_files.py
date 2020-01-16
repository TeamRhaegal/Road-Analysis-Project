#!/usr/bin/env python
# coding=utf-8

import sys, os
import glob


input_path = "/home/vincent/Documents/Travail/INSA_T/5e_annee/ProjetSIEC/github/Road-Analysis-Project/machineLearning_model/training_search/images/train/augmented_data/"
output_path = "/home/vincent/Documents/Travail/INSA_T/5e_annee/ProjetSIEC/github/Road-Analysis-Project/machineLearning_model/training_search/images/train/temp/"

image_counter = 1
xml_counter = 1

FOLDERNAME = input_path
IMAGE_FOLDER = glob.glob(FOLDERNAME+"*.jpg")
XML_FOLDER = glob.glob(FOLDERNAME+"*.xml")

for image in IMAGE_FOLDER:
    os.rename(image, os.path.join(output_path,str(image_counter)+'.jpg'))
    image_counter = image_counter +1

for csv in XML_FOLDER:
    os.rename(csv, os.path.join(output_path,str(xml_counter)+'.xml'))
    xml_counter = xml_counter +1
