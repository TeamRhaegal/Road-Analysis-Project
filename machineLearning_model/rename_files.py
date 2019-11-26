#!/usr/bin/env python
# coding=utf-8

import sys, os

input_path = 'dataset_original/'
output_path = "dataset/"


i = 1

for filename in os.listdir(input_path):
    os.rename(os.path.join(input_path,filename), os.path.join(output_path,str(i)+'.jpg'))
    i = i +1
