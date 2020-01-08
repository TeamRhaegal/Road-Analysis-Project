#!/bin/bash

lxterminal --command="/bin/bash -c 'export PYTHONPATH=$PYTHONPATH:/home/pi/Documents/Tensorflow/models:/home/pi/Documents/Tensorflow/models/research:/home/pi/Documents/Tensorflow/models/research/object_detection:/home/pi/Documents/Tensorflow/models/research/slim ; sudo python /home/pi/Documents/projet_SIEC/Road-Analysis-Project/machineLearning_model/capture_image.py'"
