import Augmentor

pathImagesDir = ""
pathImagesStop = pathImagesDir+ "\stop"
pathImagesSearch = pathImagesDir+"\search"
pathImagesProhibited = pathImagesDir+"\prohibited"

listPath = [pathImagesStop, pathImagesSearch, pathImagesProhibited]

for path in listPath :
	p = Augmentor.Pipeline(path) #mettre chemin d'accès vers le dossier des images

	p.skew(probability=0.15)
	p.random_distortion(probability=0.15)
	p.rotate(probability=0.15,max_left_rotation=90, max_right_rotation=90)
	p.shear(probability=0.15)
	p.random_brightness(probability=0.15, min_factor=0.5, max_factor=1.5) 
	p.random_contrast(probability=0.10, min_factor=0.5, max_factor=1.5)
	p.zoom(probability=0.15)

	p.sample(50)



