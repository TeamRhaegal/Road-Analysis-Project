import sys
sys.path.append("/Path To /MobileNet-ssd-keras")
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint, LearningRateScheduler, EarlyStopping, ReduceLROnPlateau, TensorBoard
from keras import backend as K
from keras.models import load_model
from math import ceil
import numpy as np
from matplotlib import pyplot as plt
import tensorflow as tf

from models.ssd_mobilenet import ssd_300
from misc.keras_ssd_loss import SSDLoss, FocalLoss, weightedSSDLoss, weightedFocalLoss
from misc.keras_layer_AnchorBoxes import AnchorBoxes
from misc.keras_layer_L2Normalization import L2Normalization
from misc.ssd_box_encode_decode_utils import SSDBoxEncoder, decode_y, decode_y2
from misc.ssd_batch_generator import BatchGenerator
from keras.utils.training_utils import multi_gpu_model
import os
import keras
import argparse
os.environ['CUDA_VISIBLE_DEVICES'] = "1"


img_height = 300  # Height of the input images
img_width = 300  # Width of the input images
img_channels = 3  # Number of color channels of the input images
subtract_mean = [123, 117, 104]  # The per-channel mean of the images in the dataset
swap_channels = True  # The color channel order in the original SSD is BGR
n_classes = 20  # Number of positive classes, e.g. 20 for Pascal VOC, 80 for MS COCO
scales_voc = [0.1, 0.2, 0.37, 0.54, 0.71, 0.88,
              1.05]  # The anchor box scaling factors used in the original SSD300 for the Pascal VOC datasets
scales_coco = [0.07, 0.15, 0.33, 0.51, 0.69, 0.87,
               1.05]  # The anchor box scaling factors used in the original SSD300 for the MS COCO datasets
scales = scales_voc

aspect_ratios = [[1.0, 2.0, 0.5],
                 [1.0, 2.0, 0.5, 3.0, 1.0 / 3.0],
                 [1.0, 2.0, 0.5, 3.0, 1.0 / 3.0],
                 [1.0, 2.0, 0.5, 3.0, 1.0 / 3.0],
                 [1.0, 2.0, 0.5],
                 [1.0, 2.0, 0.5]]  # The anchor box aspect ratios used in the original SSD300; the order matters
two_boxes_for_ar1 = True
steps = [8, 16, 32, 64, 100, 300]  # The space between two adjacent anchor box center points for each predictor layer.
offsets = [0.5, 0.5, 0.5, 0.5, 0.5,
           0.5]  # The offsets of the first anchor box center points from the top and left borders of the image as a fraction of the step size for each predictor layer.
limit_boxes = False  # Whether or not you want to limit the anchor boxes to lie entirely within the image boundaries
variances = [0.1, 0.1, 0.2,
             0.2]  # The variances by which the encoded target coordinates are scaled as in the original implementation
coords = 'centroids'  # Whether the box coordinates to be used as targets for the model should be in the 'centroids', 'corners', or 'minmax' format, see documentation
normalize_coords = True

# 1: Build the Keras model

K.clear_session()  # Clear previous models from memory.

def train(args):
  model = ssd_300(mode = 'training',
                  image_size=(img_height, img_width, img_channels),
                  n_classes=n_classes,
                  l2_regularization=0.0005,
                  scales=scales,
                  aspect_ratios_per_layer=aspect_ratios,
                  two_boxes_for_ar1=two_boxes_for_ar1,
                  steps=steps,
                  offsets=offsets,
                  limit_boxes=limit_boxes,
                  variances=variances,
                  coords=coords,
                  normalize_coords=normalize_coords,
                  subtract_mean=subtract_mean,
                  divide_by_stddev=None,
                  swap_channels=swap_channels)

  

  model.load_weights(args.weight_file, by_name=True,skip_mismatch=True)


  predictor_sizes = [model.get_layer('conv11_mbox_conf').output_shape[1:3],
                     model.get_layer('conv13_mbox_conf').output_shape[1:3],
                     model.get_layer('conv14_2_mbox_conf').output_shape[1:3],
                     model.get_layer('conv15_2_mbox_conf').output_shape[1:3],
                     model.get_layer('conv16_2_mbox_conf').output_shape[1:3],
                     model.get_layer('conv17_2_mbox_conf').output_shape[1:3]]
 
  adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=5e-04)

  ssd_loss = SSDLoss(neg_pos_ratio=3, n_neg_min=0, alpha=1.0)


  model.compile(optimizer=adam, loss=ssd_loss.compute_loss)


  train_dataset = BatchGenerator(box_output_format=['class_id', 'xmin', 'ymin', 'xmax', 'ymax'])
  val_dataset = BatchGenerator(box_output_format=['class_id', 'xmin', 'ymin', 'xmax', 'ymax'])

  # 2: Parse the image and label lists for the training and validation datasets. This can take a while.

  # TODO: Set the paths to the datasets here.


  VOC_2007_images_dir = args.voc_dir_path + '/VOC2007/JPEGImages/'
  VOC_2012_images_dir = args.voc_dir_path + '/VOC2012/JPEGImages/'

  # The directories that contain the annotations.
  VOC_2007_annotations_dir = args.voc_dir_path + '/VOC2007/Annotations/'
  VOC_2012_annotations_dir = args.voc_dir_path + '/VOC2012/Annotations/'

  # The paths to the image sets.
  VOC_2007_train_image_set_filename = args.voc_dir_path + '/VOC2007/ImageSets/Main/trainval.txt'
  VOC_2012_train_image_set_filename = args.voc_dir_path + '/VOC2012/ImageSets/Main/trainval.txt'

  VOC_2007_val_image_set_filename = args.voc_dir_path + '/VOC2007/ImageSets/Main/test.txt'


  # The XML parser needs to now what object class names to look for and in which order to map them to integers.

  classes = ['background',
             'aeroplane', 'bicycle', 'bird', 'boat',
             'bottle', 'bus', 'car', 'cat',
             'chair', 'cow', 'diningtable', 'dog',
             'horse', 'motorbike', 'person', 'pottedplant',
             'sheep', 'sofa', 'train', 'tvmonitor']


  train_dataset.parse_xml(images_dirs=[VOC_2007_images_dir,
                                       VOC_2012_images_dir],
                          image_set_filenames=[VOC_2007_train_image_set_filename,
                                               VOC_2012_train_image_set_filename],
                          annotations_dirs=[VOC_2007_annotations_dir,
                                            VOC_2012_annotations_dir],
                          classes=classes,
                          include_classes='all',
                          exclude_truncated=False,
                          exclude_difficult=False,
                          ret=False)


  val_dataset.parse_xml(images_dirs=[VOC_2007_images_dir],
                        image_set_filenames=[VOC_2007_val_image_set_filename],
                        annotations_dirs=[VOC_2007_annotations_dir],
                        classes=classes,
                        include_classes='all',
                        exclude_truncated=False,
                        exclude_difficult=False,
                        ret=False
                        )



  # 3: Instantiate an encoder that can encode ground truth labels into the format needed by the SSD loss function.

  ssd_box_encoder = SSDBoxEncoder(img_height=img_height,
                                  img_width=img_width,
                                  n_classes=n_classes,
                                  predictor_sizes=predictor_sizes,
                                  min_scale=None,
                                  max_scale=None,
                                  scales=scales,
                                  aspect_ratios_global=None,
                                  aspect_ratios_per_layer=aspect_ratios,
                                  two_boxes_for_ar1=two_boxes_for_ar1,
                                  steps=steps,
                                  offsets=offsets,
                                  limit_boxes=limit_boxes,
                                  variances=variances,
                                  pos_iou_threshold=0.5,
                                  neg_iou_threshold=0.2,
                                  coords=coords,
                                  normalize_coords=normalize_coords)

  batch_size = args.batch_size

  train_generator = train_dataset.generate(batch_size=batch_size,
                                           shuffle=True,
                                           train=True,
                                           ssd_box_encoder=ssd_box_encoder,
                                           convert_to_3_channels=True,
                                           equalize=False,
                                           brightness=(0.5, 2, 0.5),
                                           flip=0.5,
                                           translate=False,
                                           scale=False,
                                           max_crop_and_resize=(img_height, img_width, 1, 3),
                                           # This one is important because the Pascal VOC images vary in size
                                           random_pad_and_resize=(img_height, img_width, 1, 3, 0.5),
                                           # This one is important because the Pascal VOC images vary in size
                                           random_crop=False,
                                           crop=False,
                                           resize=False,
                                           gray=False,
                                           limit_boxes=True,
                                           # While the anchor boxes are not being clipped, the ground truth boxes should be
                                           include_thresh=0.4)

  val_generator = val_dataset.generate(batch_size=batch_size,
                                           shuffle=True,
                                           train=True,
                                           ssd_box_encoder=ssd_box_encoder,
                                           convert_to_3_channels=True,
                                           equalize=False,
                                           brightness=(0.5, 2, 0.5),
                                           flip=0.5,
                                           translate=False,
                                           scale=False,
                                           max_crop_and_resize=(img_height, img_width, 1, 3),
                                           # This one is important because the Pascal VOC images vary in size
                                           random_pad_and_resize=(img_height, img_width, 1, 3, 0.5),
                                           # This one is important because the Pascal VOC images vary in size
                                           random_crop=False,
                                           crop=False,
                                           resize=False,
                                           gray=False,
                                           limit_boxes=True,
                                           # While the anchor boxes are not being clipped, the ground truth boxes should be
                                           include_thresh=0.4)
  # Get the number of samples in the training and validations datasets to compute the epoch lengths below.
  n_train_samples = train_dataset.get_n_samples()
  n_val_samples = val_dataset.get_n_samples()



  def lr_schedule(epoch):
      if epoch <= 300:
          return 0.001
      else:
          return 0.0001


  learning_rate_scheduler = LearningRateScheduler(schedule=lr_schedule)
   
  checkpoint_path = args.checkpoint_path + "/ssd300_epoch-{epoch:02d}.h5"

  checkpoint = ModelCheckpoint(checkpoint_path)
  
  log_path = args.checkpoint_path + "/logs"

  tensorborad = TensorBoard(log_dir=log_path,
                            histogram_freq=0, write_graph=True, write_images=False)



  callbacks = [checkpoint,tensorborad,learning_rate_scheduler]

  # TODO: Set the number of epochs to train for.
  epochs = args.epochs
  intial_epoch = args.intial_epoch

  history = model.fit_generator(generator=train_generator,
                                steps_per_epoch=ceil(n_train_samples)/batch_size,
                                verbose=1,
                                initial_epoch=intial_epoch,
                                epochs=epochs,
                                validation_data=val_generator,
                                validation_steps=ceil(n_val_samples)/batch_size,
                                callbacks=callbacks
                                )





if __name__== "__main__":
    parser = argparse.ArgumentParser(description='Evaluation script')
    parser.add_argument('--voc_dir_path', type=str,
                        help='VOCdevkit directory path')
    parser.add_argument('--weight_file',type=str,
                        help='weight file path')
    parser.add_argument('--epochs',type=int,
                        help='Number of epochs', default = 500)
    parser.add_argument('--intial_epoch',type=int,
                        help='intial_epoch', default=0)
    parser.add_argument('--checkpoint_path',type=str,
                        help='Path to save checkpoint')
    parser.add_argument('--batch_size',type=int,
                        help='batch_size', default=32)

    args = parser.parse_args()
    train(args)
