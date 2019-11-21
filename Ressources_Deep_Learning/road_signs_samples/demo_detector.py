#!/usr/bin/env python
# coding=utf-8

"""
    Optimised code that allows to detect road signs from an image and classify them, using two distincts machine learning models : 
        - Fast R-CNN / Mobilenet SSD model for traffic sign location
        - a classic CNN (Convulotionnal Neural Netork) for road sign classification (stop, speed limit, prohibited way, etc.)
"""

from tqdm import tqdm


print("Importing libraries")
for i in tqdm(range(1000)):
    # system imports 
    import sys, os, time, traceback, psutil
    from threading import Thread, Lock
    # image processing imports
    from skimage import io, color, exposure, transform
    from PIL import Image
    import cv2
    # arrays processing imports
    import numpy as np


    sys.path.append('roadsign_python_source/')
    from roadsign_python_source import location, classification

    RASPICAM_ENABLE = False
    if (RASPICAM_ENABLE):
        from roadsign_python_source import raspicam
        
    # define if we want to draw rectangles around ROIs and save corresonding images (for DEBUG purposes)
    DRAW = True

"""
    Define different paths for example images, location and classification model, etc.
"""
PATH_FOR_EXAMPLE_IMAGE = "images/00074.ppm"
PATH_TO_LOCATION_MODEL = "F_RCNN_location/mobilenet_v1/rfcn_resnet101_gtsdb3.config"
PATH_TO_CKPT = "F_RCNN_location/mobilenet_v1/frozen_inference_graph.pb"
PATH_TO_LABELS = "F_RCNN_location/scripts/gtsdb_label_map.pbtxt"
NUM_CLASSES = 3

PATH_TO_CLASSIFICATION_MODEL = "classification_model.h5"


"""
    GLOBAL SHARED VARIABLES WITH FUTURE PROGRAMS
"""
# all different road signs detected, as array of int (one int represent one category for one roadsign)
CLASSIFICATION_RESULT = []


"""
    GLOBAL LOCK VARIABLES, LINKED TO SHARED VARIABLES
"""
LOCK_CLASSIFICATION_RESULT = Lock()

"""
    OBJECT INSTANCES AND CONSTANTS
        - roadsign_types : meaning of each 43 classes of road signs, and a path to an image of each road sign
"""
roadsign_types = [  ["speed limit 20",                                  "images/roadsigns_representation/00000/speed_limit_20.ppm"],
                    ["speed limit 30",                                      "images/roadsigns_representation/00001/speed_limit_30.ppm"],
                    ["speed limit 50",                                      "images/roadsigns_representation/00002/speed_limit_50.ppm"],
                    ["speed limit 60",                                      "images/roadsigns_representation/00003/speed_limit_60.ppm"],
                    ["speed limit 70",                                      "images/roadsigns_representation/00004/speed_limit_70.ppm"],
                    ["speed limit 80",                                      "images/roadsigns_representation/00005/speed_limit_80.ppm"],
                    ["end of speed limit 80",                           "images/roadsigns_representation/00006/end_speed_limit_80.ppm"],
                    ["speed limit 100",                                     "images/roadsigns_representation/00007/speed_limit_100.ppm"],
                    ["speed limit 120",                                     "images/roadsigns_representation/00008/speed_limit_120.ppm"],
                    ["forbidden to overtake car",                "images/roadsigns_representation/00009/forbidden_overtake.ppm"],
                    ["forbidden for truck to overtake",             "images/roadsigns_representation/00010/forbidden_overtake_truck.ppm"],
                    ["priority for the next cross",                     "images/roadsigns_representation/00011/priority_road_sign.ppm"],
                    ["priority road",                                           "images/roadsigns_representation/00012/priority_sign.ppm"],
                    ["give way",                                                "images/roadsigns_representation/00013/let_priority_sign.ppm"],
                    ["stop",                                                        "images/roadsigns_representation/00014/stop.ppm"],
                    ["forbidden for motored vehicles",              "images/roadsigns_representation/00015/forbidden_motored_vehicle.ppm"],
                    ["forbidden for trucks",                                "images/roadsigns_representation/00016/forbidden_truck.ppm"],
                    ["prohibited way",                                          "images/roadsigns_representation/00017/prohibited_way.ppm"],
                    ["warning",                                                     "images/roadsigns_representation/00018/warning.ppm"],
                    ["dangerous turn left",                                 "images/roadsigns_representation/00019/dangerous_turn_left.ppm"],
                    ["dangerous turn right",                                "images/roadsigns_representation/00020/dangerous_turn_right.ppm"],
                    ["multiple turn left",                                      "images/roadsigns_representation/00021/multiple_turn_left.ppm"],
                    ["bump ahead",                                          "images/roadsigns_representation/00022/bump.ppm"],
                    ["warning slippy road",                                 "images/roadsigns_representation/00023/warning_slip.ppm"],
                    ["tighter way right",                                       "images/roadsigns_representation/00024/tighter_way_right.ppm"],
                    ["road works ahead",                                    "images/roadsigns_representation/00025/roadworks.ppm"],
                    ["traffic light ahead",                                     "images/roadsigns_representation/00026/traffic_light.ppm"],
                    ["warning pedestrian",                                  "images/roadsigns_representation/00027/warning_pedestrian.ppm"],
                    ["warning childs",                                          "images/roadsigns_representation/00028/warning_pedestrian_child.ppm"],
                    ["warning bycicles",                                        "images/roadsigns_representation/00029/warning_bycicle.ppm"],
                    ["presence of snow",                                    "images/roadsigns_representation/00030/warning_snow.ppm"],
                    ["warning wild animals",                                "images/roadsigns_representation/00031/warning_wild_animal.ppm"],
                    ["enf of last speed limit",                                 "images/roadsigns_representation/00032/end_last_speed_limit.ppm"],
                    ["indication : turn right",                                 "images/roadsigns_representation/00033/indication_right_turn.ppm"],
                    ["indication : turn left",                                  "images/roadsigns_representation/00034/indication_left_turn.ppm"],
                    ["indication : straight line",                          "images/roadsigns_representation/00035/indication_straight_line.ppm"],
                    ["indication : straight + right",                       "images/roadsigns_representation/00036/indication_straight_right.ppm"],
                    ["indication : straight + left",                        "images/roadsigns_representation/00037/indication_straight_left.ppm"],
                    ["go right side",                                               "images/roadsigns_representation/00038/go_right_mandatory.ppm"],
                    ["go left side",                                                "images/roadsigns_representation/00039/go_left_mandatory.ppm"],
                    ["roundabout ahead",                                    "images/roadsigns_representation/00040/roundabout.ppm"],
                    ["end of forbidden overtake for cars",              "images/roadsigns_representation/00041/end_forbidden_overtake.ppm"],
                    ["end of forbidden overtake for trucks",            "images/roadsigns_representation/00042/end_forbidden_overtake_truck.ppm"]
                ]

def roadsign_detector():
    global CLASSIFICATION_RESULT
    """
    Remove Python cache files if they exist
    """
    os.system("rm -rf  roadsign_python_source/*.pyc && rm -rf roadsign_python_source/keras_frcnn/*.pyc")
    
    # init camera or example image depending on the mode chosen
    if (RASPICAM_ENABLE):
        #init camera from raspberry (raspicam)
        camera = raspicam.Raspicam()
    else:
        # load example image 
        location_input_image = io.imread(PATH_FOR_EXAMPLE_IMAGE)
        io.imsave("images/runtime/camera/raspicam_captured.jpg", location_input_image)
        
    # create instance of both location and classification model, and load models
    #print("loading location model")
    #for i in tqdm(range(1000)): 
    location_model = location.LocationModel(debug=False)
    location_model.load_model(model_path=PATH_TO_LOCATION_MODEL, ckpt_path=PATH_TO_CKPT, label_path=PATH_TO_LABELS, num_classes=NUM_CLASSES)
    
    #print("\nloading classification model")
    #for i in tqdm(range(1000)):
    classification_model = classification.ClassificationModel(debug=False)
    classification_model.load_model(model_path=PATH_TO_CLASSIFICATION_MODEL)

    # main loop : 
    while(1):
        try:
            if (RASPICAM_ENABLE):
                camera.capture_image()
                location_input_image = camera.read_image_as_numpy_array(save=True)
            
            # now, find the location of road signs on the image
            img = location_input_image.copy()
            location_boxes, location_score = location_model.detect_roadsigns_from_numpy_array(img)
            
            """
                Next part of code :
                    - save each box were the probability score is better than a defined threshold 
                    - crop the image from each saved Region of Interest (ROI)
                    - pre process cropped image in order to use it in the the classification model 
                    - process image into classification model and add class result in the "classification_result" array
                If DEBUG is True, print, save and show image with all the boxes rendered. 
            """
            # Variable that contains classification result for all the "interesting" images found in the big image
            classification_result = []
            
            for i in range(location_boxes.shape[1]):
                if (location_score[0][i] > 0.04):
                    # crop interesting  part (box) from the global image
                    x1 = int(location_boxes[0][i][1]*location_input_image.shape[1])
                    x2 = int(location_boxes[0][i][3]*location_input_image.shape[1])
                    y1 = int(location_boxes[0][i][0]*location_input_image.shape[0])
                    y2 = int(location_boxes[0][i][2]*location_input_image.shape[0])
                    img = location_input_image[y1:y2, x1:x2]
                    
                    io.imsave("cropped_image_"+str(i)+".png", img) 
                    print("saved cropped image {}".format(i))
                    
                    # pre process image in order to use it in the classification model
                    preprocessed_img =  classification_model.preprocess_img(img)
                    
                    #io.imsave("preprocessed_image_"+str(i)+".png", preprocessed_img)
                    classification_result.append(classification_model.predict_result(preprocessed_img))
                    print("result = {}".format(classification_model.predict_result(preprocessed_img)))
                    
                    if (DRAW):
                        # draw rectangle boxes around Region of Interest (ROI)
                        cv2.rectangle(location_input_image, (x1,y1), (x2,y2), (255,0,0), 1)
                        io.imsave("image_with_ROIs.png", location_input_image)
                       
            # save result in the global variable (acquire lock then release it after modifying variable
            LOCK_CLASSIFICATION_RESULT.acquire()
            CLASSIFICATION_RESULT = classification_result[:]
            LOCK_CLASSIFICATION_RESULT.release()
            print("result found and saved")
            
        except KeyboardInterrupt :
            print("\nCTRL+C PRESSED : CLOSING PROGRAM")
            sys.exit()
    pass


"""
        MAIN FUNCTION
"""
if __name__ == "__main__":

    try : 
        thread_roadsign_detector = Thread(target=roadsign_detector)
        thread_roadsign_detector.start()
    except KeyboardInterrupt : 
        print("\nCTRL+C PRESSED : CLOSING PROGRAM")
        sys.exit()
    pass
    
    
    
     
    
