#!/usr/bin/env python
# coding=utf-8

"""
    Optimised code that allows to detect road signs from an image and classify them, using one machine learning model (CNN for classification) and shape detection using openCV to 
        - Fast R-CNN / Mobilenet SSD model for traffic sign location
        - a classic CNN (Convulotionnal Neural Netork) for road sign classification (stop, speed limit, prohibited way, etc.)
"""

import time

print("Importing libraries")
begin = time.time()
# system imports 
import sys, os, time, traceback
from threading import Thread, Lock
# image processing imports
from skimage import io
import cv2, imutils
# arrays processing imports
import numpy as np

sys.path.append('roadsign_python_source/')
from roadsign_python_source import location_shapes, classification

RASPICAM_ENABLE = True
if (RASPICAM_ENABLE):
    from roadsign_python_source import raspicam
    
print("imported libraries : ellapsed time : {} s".format(time.time() - begin))
      
# define if we want to draw rectangles around ROIs and save corresonding images (for DEBUG purposes)
DRAW = True

"""
    Define different paths for example images, location and classification model, etc.
"""
PATH_FOR_EXAMPLE_IMAGE = "images/stoptest.ppm"
PATH_TO_CLASSIFICATION_MODEL = "classification_model.h5"

"""
    GLOBAL SHARED VARIABLES WITH FUTURE PROGRAMS
"""
# all different road signs detected, as array of int (one int represent one category for one roadsign)
sign = "None"
# size of cropped image, containing only roadsign
signWidth = None

"""
    GLOBAL LOCK VARIABLES, LINKED TO SHARED VARIABLES
"""
signLock = Lock()
signWidthLock = Lock()

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


    try : 
        global sign, signWidth, PATH_FOR_EXAMPLE_IMAGE, PATH_TO_CLASSIFICATION_MODEL
        
        print("initializing roadsign detector")
        init_time = time.time()
        #Remove Python cache files if they exist
        os.system("rm -rf  roadsign_python_source/*.pyc && rm -rf roadsign_python_source/keras_frcnn/*.pyc")
    
        # init camera or example image depending on the mode chosen
        if (RASPICAM_ENABLE):
            #init camera from raspberry (raspicam)
            print("initializing camera")
            camera = raspicam.Raspicam()
        else:
            # load example image 
            print("loading example image (not camera)")
            location_input_image = cv2.imread(PATH_FOR_EXAMPLE_IMAGE)    
            
            if(DRAW):
                cv2.imshow("image", location_input_image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        
        # define location object instance
        location_model = location_shapes.LocationShapes(draw=DRAW)
        
        # load classification model
        print("loading classification model")
        classification_model = classification.ClassificationModel(debug=DRAW)
        classification_model.load_model(model_path=PATH_TO_CLASSIFICATION_MODEL)

        print ("initialized roadsign detector. Ellapsed time : {} s".format(time.time()-init_time))
        """
            MAIN LOOP
        """
        while(1):
            # count time taken to process one image. Can vary depending on the number of contours detected.
            print("capturing image, then process location and classification")
            process_time = time.time()
            
            if (RASPICAM_ENABLE):
                camera.capture_image()
                location_input_image = camera.read_image_as_numpy_array(save=True)
                location_input_image = cv2.cvtColor(location_input_image, cv2.COLOR_RGB2BGR)
                                
            # now, find the location of road signs on the image
            location_model.process_image(location_input_image)
            contours = location_model.process_contours()
            print ("processed contours. Number of contours : {}".format(len(contours)))
            # for each contour, verify that it is a "real" road sign or at least a known shape
            for c in contours:
                # find coordinates of "interesting" boxes : 
                    # x = upper left x coordinate
                    # y = upper left y coordinate
                    # w = width of the box
                    # h = heigh of the box
                x, y, w, h = location_model.find_shape_box(c)
                #print("x : {}, y : {}, w : {}, h : {}".format(x,y,w,h))
                if (x != -1 or y != -1 or w != -1 or h != -1):
                    cropped_image = location_input_image[y:y+h, x:x+w].copy()
                    
                    if (DRAW):
                        cv2.imshow("image", cropped_image)
                        cv2.waitKey(0)
                        cv2.destroyAllWindows()
                        
                    # change cropped image to RGB format (and no more BGR)
                    cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
                    # preprocess image for classification
                    preprocessed_image = classification_model.preprocess_img(cropped_image)
                    # find predictions about image
                    predictions = classification_model.show_result_probabilities(preprocessed_image)
                    
                    if(max(predictions[0])) >= 0.2:
                        result = classification_model.predict_result(preprocessed_image)
                        print("detected road sign : {}".format(roadsign_types[result][0]))
                        
                        if (result == 14):
                            print("LA VOITURE DOIT S'ARRETER ! ")
                        
                        # save result in global variable
                        signLock.acquire()
                        sign = roadsign_types[result][0] 
                        signLock.release()
                        
                        signWidthLock.acquire()
                        signWidth = w
                        signWidthLock.release()
                        
                        time.sleep(0.1)
                        
                    
            print("processed road sign location and classification. Ellapsed time : {}".format(time.time()-process_time))
            time.sleep(1)
            
    except KeyboardInterrupt:
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
    
    
    
     
    
