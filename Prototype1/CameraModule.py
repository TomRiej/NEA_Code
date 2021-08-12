  # Requirements
# getReadSuccess()
# getCarInfo()
# only 2 frames taken from camera

import cv2 as cv
import numpy as np
from time import time
from math import sqrt
from heapq import nsmallest

# DEBUG = True

class CameraInput:
    def __init__(self):
        # Initializing constants
        self.__GREEN = 0
        self.__ORANGE = 1
        self.__BLUE = np.array([254, 81, 20], dtype=np.uint8)
        self.__LOADING_DOTS_X_COORDS = [932, 959, 985]
        self.__DESLOT_THRESHOLD = 0
        
        # initializing OpenCV objects
        self.__cameraFeed = cv.VideoCapture(1)
        self.__backgroundSubtractor = cv.createBackgroundSubtractorMOG2(detectShadows=False)
        self.__detector = cv.SimpleBlobDetector_create()
        
    def checkCameraIsConnected(self):
        # if the image has the three blue loading dots,
        # then the camera is not connected
        results = []
        for _ in range(3):
            frame = self.__readFrame()
            blueMask = cv.inRange(frame, self.__BLUE, self.__BLUE)
            blueMask = cv.bitwise_not(cv.blur(blueMask, (5,5)))
            loadingDots = self.__detector.detect(blueMask)
            xs = []
            for dot in loadingDots:
                xs.append(int(dot.pt[0]))
            
            if sorted(xs) == self.__LOADING_DOTS_X_COORDS:
                results.append(False)
            else:
                results.append(True)
        
        if sum(results) > 1: # majority of frames had no dots
            return True
        else:
            return False
        
    # def showAFrame(self):
    #     while True:
    #         cv.imshow("Test Frame", self.__readFrame())
    #         key = cv.waitKey(1)
    #         if key == 27:
    #             break 
                
        
    def __readFrame(self):
        successful, frame = self.__cameraFeed.read()
        if successful:
            return frame
        else:
            print("Frame could not be read")
            return None
        
if __name__ == '__main__':
    cam = CameraInput()
    for i in range(300):
        if cam.checkCameraIsConnected():
            print(i, "connected")