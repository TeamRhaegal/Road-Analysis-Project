 In this folder you will find ressources used to train a model to recognize road signs from raspicam datasets. 
 
the datasets were made with the raspicam on the front of the car, to train a model as accurate as possible and as efficient as possible on this equipment precisely. 

The "training X" folders are always made in the same way. Indeed they are copied into the "Tensorflow" folder of the computer following the tutorial presented (https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/). 

TensorFlow
├─ addons
│   └─ labelImg
├─ models
│   ├─ official
│   ├─ research
│   ├─ samples
│   └─ tutorials
└─ workspace            ---> "TRAINING X" FOLDERS SHOULD GO IN THIS FOLDER
    └─ training_demo   
    
From this folder, different models can be trained depending on the chosen configuration. 

The "good_model X" folders contain checkpoints of interest for each type of model, as well as a backup of the inference graph, an essential element used to make predictions from the trained model. 

The "config_model" folder contains copies of different configurations, such as the architecture of the models used, or the class tree.
