#!/usr/bin/env python
# coding=utf-8

import sys, os

input_path = "/home/vincent/Documents/Travail/INSA_T/5e_annee/ProjetSIEC/github/Road-Analysis-Project/machineLearning_model/training_search/images/train"
output_path = "/home/vincent/Documents/Travail/INSA_T/5e_annee/ProjetSIEC/github/Road-Analysis-Project/machineLearning_model/training_search/images/sorted_train/"


i = 1

for filename in os.listdir(input_path):
    os.rename(os.path.join(input_path,filename), os.path.join(output_path,str(i)+'.jpg'))
    i = i +1
