#!/usr/bin/env python
# coding=utf-8

import sys, os

path = 'dataset_original/'
i = 1
for filename in os.listdir(path):
    os.rename(os.path.join(path,filename), os.path.join(path,str(i)+'.jpg'))
    i = i +1
