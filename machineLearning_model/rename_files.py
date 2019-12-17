#!/usr/bin/env python
# coding=utf-8

import sys, os

input_path = '/home/vincent/Documents/INSA/5A/Projet_SIEC/Road-Analysis-Project/machineLearning_model/training_search/images/augmented_data/output/'
output_path = "/home/vincent/Documents/INSA/5A/Projet_SIEC/Road-Analysis-Project/machineLearning_model/training_search/images/final_augmented_data/"


i = 283

for filename in os.listdir(input_path):
    os.rename(os.path.join(input_path,filename), os.path.join(output_path,str(i)+'.jpg'))
    i = i +1
