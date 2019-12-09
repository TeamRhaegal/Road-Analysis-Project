import Augmentor

p = Augmentor.Pipeline("D:\\INSA\\5e\\projetRhaegal\\Road-Analysis-Project\\machineLearning_model\\trainingV1_original\\images\\train") #mettre chemin d'accès vers le dossier des images

p.skew(probability=0.20)
#p.random_distortion(probability=0.15)
p.rotate(probability=0.20,max_left_rotation=10, max_right_rotation=10)
p.shear(probability=0.20,max_shear_left=10,max_shear_right=10)
p.random_brightness(probability=0.15, min_factor=0.5, max_factor=1.5) 
p.random_contrast(probability=0.10, min_factor=0.5, max_factor=1.5)
p.zoom(probability=0.15,min_factor=50,max_factor=50)


# Now we can sample from the pipeline:
p.sample(50)



