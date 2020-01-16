#!/usr/bin/env python
# coding=utf-8

import Augmentor

p = Augmentor.Pipeline(unicode("/home/vincent/Documents/Travail/dummywork/")) #mettre chemin d'accès vers le dossier des images


p.skew(probability=0.2)
#p.random_distortion(probability=0.15)
p.rotate(probability=0.20,max_left_rotation=5, max_right_rotation=5)
p.shear(probability=0.20,max_shear_left=5,max_shear_right=5)
p.random_brightness(probability=0.15, min_factor=0.5, max_factor=1.5) 
p.random_contrast(probability=0.10, min_factor=0.5, max_factor=1.5)
#p.zoom(probability=0.15,min_factor=50,max_factor=50)
p.flip_left_right(probability=0.20)
# Now we can sample from the pipeline:
p.sample(350)


"""
p.skew(probability=1)
#p.random_distortion(probability=0.15)
p.rotate(probability=1,max_left_rotation=25, max_right_rotation=25)
p.shear(probability=1,max_shear_left=25,max_shear_right=25)
p.random_brightness(probability=0.8, min_factor=0.1, max_factor=5) 
p.random_contrast(probability=0.8, min_factor=0.1, max_factor=5)
#p.zoom(probability=0.15,min_factor=50,max_factor=50)
p.flip_left_right(probability=0.5)
# Now we can sample from the pipeline:
p.sample(200)
"""


