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
from sklearn.cross_validation import train_test_split

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
from keras.optimizers import SGD
from keras.utils import np_utils
from keras.callbacks import LearningRateScheduler, ModelCheckpoint
from keras import backend as K
K.set_image_data_format('channels_first')

# graphical representation imports
from matplotlib import pyplot as plt
%matplotlib inline

# number of different signs in the dataset
NUM_CLASSES = 43
# squared image size we want (lenght X height) : The larger the image (high resolution), the longer the calculations will be.
IMG_SIZE = 48

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
