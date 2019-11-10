#!/usr/bin/env python

"""
Authors :
    code : https://github.com/chsasank/Traffic-Sign-Classification.keras
    comments / modifications : Vincent Pinel

Program used to train a model for recognizing and classifying traffic signs, based on German sign samples (http://benchmark.ini.rub.de/)
The selected neural network model is a 6-layer convolutional network (classic).

This code is pedagogical and commented to understand each line.

The tools used are:
- Keras to train the model in a simple way
- pandas, skimage for image processing and pre-processing.
"""

# image processing imports
import numpy as np
from skimage import io, color, exposure, transform
from sklearn.model_selection import train_test_split

# system imports
import os
import glob     # glob allows to capture multiple file paths in one array of paths (useful in our case, for image dataset opening (about 51 000 files))
import h5py     # h5py allows to save trained models in HDF5 file format : more information here : https://www.h5py.org/

# model training and processing imports
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential, model_from_json
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Conv2D
from keras.layers.pooling import MaxPooling2D

# training and test imports
import pandas as pd
from keras.optimizers import SGD
from keras.utils import np_utils
from keras.callbacks import LearningRateScheduler, ModelCheckpoint
from keras import backend as K
K.set_image_data_format('channels_first')

# graphical representation imports
#from matplotlib import pyplot as plt
#exec(%matplotlib inline)

# number of different signs in the dataset
NUM_CLASSES = 43
# squared image size we want (lenght X height) : The larger the image (high resolution), the longer the calculations will be.
IMG_SIZE = 48
# Data augmentation defines if we want to create new images from existing images
# for example take an image of a stop sign and copy it multiple times with different characteristics (contrast, light, saturation, angle...)
DATA_AUGMENTATION = False

"""
    Function used to :
        - equalize the histogram (contrast) of the image : (convert to HSV format, then normalize the Y axis (light values), and finally convert back to RGB)
        - crop image to its center (most part of the image)
        - rescale image to IMG_SIZE x IMG_SIZE size.

    input : image (RGB numpy array)
    output : processed image (RGB numpy array)
"""
def preprocess_img(img):
    # Histogram normalization in y
    hsv = color.rgb2hsv(img)
    hsv[:,:,2] = exposure.equalize_hist(hsv[:,:,2])     # equalize_hist(image, nbins=256, mask=None) : return image array as HSV : (Hue (degrees), saturation (%), value (%))
    img = color.hsv2rgb(hsv)

    # central scrop
    min_side = min(img.shape[:-1])
    centre = img.shape[0]//2, img.shape[1]//2
    img = img[centre[0]-min_side//2:centre[0]+min_side//2,
              centre[1]-min_side//2:centre[1]+min_side//2,
              :]

    # rescale to standard size
    img = transform.resize(img, (IMG_SIZE, IMG_SIZE))

    # roll color axis to axis 0
    img = np.rollaxis(img,-1)

    return img

"""
    function that returns the class of any road sign image, knowing its path
"""
def get_class(img_path):
    return int(img_path.split('/')[-2])

"""
    function "cnn_model" : see http://neuralnetworksanddeeplearning.com/chap6.html#introducing_convolutional_networks for more informations about CNNs
        - define convolutional model using Keras library : features :
            - Sequential successive layers : https://keras.io/getting-started/sequential-model-guide/

    Conv2D function parameters (same order as in the function, see below):
        - filter : integer : dimensionality of the output space (i.e. the number of output filters in the convolution).
        - kernel : tuple of 2 integers (x,y) : specifying the height and width of the 2D convolution window. Can be a single integer to specify the same value for all spatial dimensions.
        - strides : tuple of 2 integers : NOT INDICATED IN THIS PROGRAM ! (specifying the strides of the convolution along the height and width)
        - padding : one of "valid" or "same" (case-insensitive)
        - Input shape : 4D tensor with shape: (batch, channels, rows, cols) if data_format is "channels_first" (our case)
        - activation : Activation function to use (available : elu, softmax, selu, softplus, softsign, relu)

    MaxPooling2D function parameters : Max pooling operation for spatial data.
        - pool_size = integer or tuple of 2 integers, factors by which to downscale (vertical, horizontal). (2, 2) will halve the input in both spatial dimension. If only one integer is specified, the same window length will be used for both dimensions.

    Dropout function arguments : Applies Dropout to the input. Dropout consists in randomly setting a fraction rate of input units to 0 at each update during training time, which helps prevent overfitting.
        - rate : float between 0 and 1. Fraction of the input units to drop.

    Dense function arguments : Just your regular densely-connected NN layer. Dense implements the operation: output = activation(dot(input, kernel) + bias) where activation is the element-wise activation function passed as the activation argument, kernel is a weights matrix created by the layer, and bias is a bias vector created by the layer (only applicable if use_bias is True).
        - units : Positive integer, dimensionality of the output space.
        - activation : Activation function to use (available : elu, softmax, selu, softplus, softsign, relu)

    Flatten function : Flattens the input. Does not affect the batch size.


"""
def cnn_model():
    model = Sequential()

    # first layer
    model.add(Conv2D(32, (3, 3), padding='same',
                     input_shape=(3, IMG_SIZE, IMG_SIZE),     # input of the first layer : it is the image.
                     activation='relu'))
    model.add(Conv2D(32, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.2))

    model.add(Conv2D(64, (3, 3), padding='same',
                     activation='relu'))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.2))

    model.add(Conv2D(128, (3, 3), padding='same',
                     activation='relu'))
    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.2))

    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(NUM_CLASSES, activation='softmax'))         # outpout of the last layers : 43 classes (all different road sign classes), it is a probability tree
    return model

"""
    Learning rate schedule function
"""
def lr_schedule(epoch):
    return lr*(0.1**int(epoch/10))

"""
    Next paragraph :
        - create a "new" training set from the dataset files (in one array so it is easy to manipulate)
        - shuffle all files in order to train model to recognise random road sign images (and not a sequence of the same signs)
        - Pre process all images from the dataset
        - Assign the corresponding label for each image (file path)
        - create "imgs" (RGB) and "labels" (int) arrays  to store associate an image to its class

        - convert "imgs" array to an universal readable format : float 32
        - create a diagonal matrix of 1 (and 0 elsewhere), while pointing on one "label" row

"""

if __name__ == "__main__":

    root_dir = 'GTSRB/Final_Training/Images/'
    imgs = []
    labels = []

    all_img_paths = glob.glob(os.path.join(root_dir, '*/*.ppm'))        # capture all the image file paths ('*/*.ppm' files) in a 1D array (have all the dataset file paths in only one array)
    np.random.shuffle(all_img_paths)                                    # shuffle all images path (in order to have random road sign and not the same roadsings for a big number of images)
    for img_path in all_img_paths:
        try:
            img = preprocess_img(io.imread(img_path))                   # io imread from skimage read image from file and return RGB array
            label = get_class(img_path)
            imgs.append(img)
            labels.append(label)
            if len(imgs)%1000 == 0: print("Processed {}/{}".format(len(imgs), len(all_img_paths)))      # progression bar
        except (IOError, OSError):
            print('missed', img_path)
            pass

    X = np.array(imgs, dtype='float32') # convert images array to universal format float 32
    # Make one hot targets
    Y = np.eye(NUM_CLASSES, dtype='uint8')[labels]  # matrix of "num NUM_CLASSES x NUM_CLASSES". Contains the number "1" in diagonal. "[labels]" point on a certain row of this matrix
    print("\nImage processed and new dataset created !")

    """
        Train the model using SGD : Stochastic gradient descent optimizer. Includes support for momentum, learning rate decay, and Nesterov momentum.
        arguments :
                - learning rate (lr) : float >= 0, 0.01 by default
                - momentum : float >= 0. Parameter that accelerates SGD in the relevant direction and dampens oscillations.
                - nesterov : boolean. Whether to apply Nesterov momentum.

        model compile function : arguments :
                - A loss function. This is the objective that the model will try to minimize. It can be the string identifier of an existing loss function (such as categorical_crossentropy or mse), or it can be an objective function
                - An optimizer. This could be the string identifier of an existing optimizer (such as rmsprop or adagrad), or an instance of the Optimizer class.
                - A list of metrics. For any classification problem you will want to set this to metrics=['accuracy'].
    """

    model = cnn_model()
    # let's train the model using SGD + momentum
    lr = 0.01
    sgd = SGD(lr=lr, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy',
              optimizer=sgd,
              metrics=['accuracy'])

    print("\nModel Compiled !")
    batch_size = 32
    epochs = 30

    """
        model fit function : Trains the model for a fixed number of epochs (iterations on a dataset).
            arguments :
                - batch_size: Integer or None. Number of samples per gradient update. If unspecified, batch_size will default to 32
                - epochs: Integer. Number of epochs to train the model. An epoch is an iteration over the entire x and y data provided
                - validation_split: Float between 0 and 1. Fraction of the training data to be used as validation data.
                - callbacks : List of keras.callbacks.Callback instances. List of callbacks to apply during evaluation.
                                Allows to save the model during the time, here using "hdf5" format
    """
    model.fit(X, Y,
              batch_size=batch_size,
              epochs=epochs,
              validation_split=0.2,
              callbacks=[LearningRateScheduler(lr_schedule),
                         ModelCheckpoint('model.h5', save_best_only=True)]  # pass to save checkpoints of trained model on the hard drive disk
              )

    print ("\nModel Fitted !")

    """
        Load test data, verify the model and print the accuracy of the model
            - read csv file containing for each image :
                    - its name (reference : 'Filename')
                    - its class id (reference : 'ClassID')
            - create a new dataset:
                    - for each image, save its value (RGB) + its class id
            - test the model using 'predict_classes' function
            - print the recognition accuracy (in percentage) : sum of (prediction == test value) / total number of test values
    """
    test = pd.read_csv('GTSRB/GT-final_test.csv',sep=';')

    X_test = []
    y_test = []
    i = 0
    for file_name, class_id  in zip(list(test['Filename']), list(test['ClassId'])):
        img_path = os.path.join('GTSRB/Final_Test/Images/',file_name)
        X_test.append(preprocess_img(io.imread(img_path)))
        y_test.append(class_id)

    X_test = np.array(X_test)
    y_test = np.array(y_test)

    y_pred = model.predict_classes(X_test)
    acc = np.sum(y_pred==y_test)/np.size(y_pred)
    print("Test accuracy = {}".format(acc))

    # final save of the model
    model.save("model.h5")

    """
        Next paragraph process data augmentation.
        The objective is to create a dataset larger than the provided dataset, by taking existing images and duplicating them.
        For each duplication, the image characteristics are modified so that the model can recognize signs in as many situations as possible (night, day, fog, light effects...)
        In the end, starting from a model trained on 50,000 images, we will be able to arrive at a model trained with more than 100,000 images.
        This improves the accuracy of the model by modifying the variables in the neural network.

            sklearn 'train_test_split' function : Split arrays or matrices into random train and test subsets
            - test_size : If float, should be between 0.0 and 1.0 and represent the proportion of the dataset to include in the test split.
            - random_state : If int, random_state is the seed used by the random number generator

            Keras 'ImageDataGenerator' function : Generate batches of tensor image data with real-time data augmentation. The data will be looped over (in batches).
                - featurewise_center : Boolean. Set input mean to 0 over the dataset, feature-wise.
                - featurewise_std_normalization : Boolean. Divide inputs by std of the dataset, feature-wise.
                - width_shift_range : Float, 1-D array-like or int
                                        - float: fraction of total width, if < 1, or pixels if >= 1.
                - zoom_range : Float or [lower, upper]. Range for random zoom. If a float, [lower, upper] = [1-zoom_range, 1+zoom_range].
                - shear_range : Float. Shear Intensity (Shear angle in counter-clockwise direction in degrees)
                - rotation_range : Int. Degree range for random rotations.
    """
    if (DATA_AUGMENTATION):
        # next line split arrays or matrices into random train and test subsets
        # parameters : Arrays (X,Y) of data,
        X_train, X_val, Y_train, Y_val = train_test_split(X, Y, test_size=0.2, random_state=42)

        datagen = ImageDataGenerator(featurewise_center=False,
                                    featurewise_std_normalization=False,
                                    width_shift_range=0.1,
                                    height_shift_range=0.1,
                                    zoom_range=0.2,
                                    shear_range=0.1,
                                    rotation_range=10.,)

        # fit generated images to the existing dataset
        datagen.fit(X_train)

        # Reinstallise models
        model = cnn_model()
        # let's train the model using SGD + momentum
        lr = 0.01
        sgd = SGD(lr=lr, decay=1e-6, momentum=0.9, nesterov=True)
        model.compile(loss='categorical_crossentropy',
                  optimizer=sgd,
                  metrics=['accuracy'])

        print("\nAugmented data model compiled !")

        nb_epoch = 30
        """
            datagen.flow function : Takes data & label arrays, generates batches of augmented data.
                - x : Input data. Numpy array of rank 4 or a tuple
                - y : Labels
                - batch_size : Int (default: 32).

            fit_generator function : Trains the model on data generated batch-by-batch by a Python generator (or an instance of Sequence).
                - generator (datagen) : A generator or an instance of Sequence (keras.utils.Sequence) object in order to avoid duplicate data when using multiprocessing
                - steps_per_epoch: Integer. Total number of steps (batches of samples) to yield from generator before declaring one epoch finished and starting the next epoch
                - epochs: Integer. Number of epochs to train the model. An epoch is an iteration over the entire data provided, as defined by steps_per_epoch
                - validation data : This can be a generator or a Sequence object for the validation data, or a tuple (x_val, y_val)
                - callbacks: List of keras.callbacks.Callback instances. List of callbacks to apply during training.
        """
        model.fit_generator(datagen.flow(X_train, Y_train, batch_size=batch_size),
                                    steps_per_epoch=X_train.shape[0],
                                    epochs=nb_epoch,
                                    validation_data=(X_val, Y_val),
                                    callbacks=[LearningRateScheduler(lr_schedule),
                                               ModelCheckpoint('model.h5',save_best_only=True)]
                                   )
        # printtest the model and check accuracy again
        y_pred = model.predict_classes(X_test)
        acc = np.sum(y_pred==y_test)/np.size(y_pred)
        print("Test accuracy = {}".format(acc))

        model.summary()

        print("\nAugmented data model fitted !")
