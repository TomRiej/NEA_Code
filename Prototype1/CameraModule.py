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
    def __init__(self, greenRange, orangeRange, deslotThreshold, sampleIters):
        # Initializing constants
        self.__GREEN = 0
        self.__ORANGE = 1
        self.__BLUE = np.array([254, 81, 20], dtype=np.uint8)
        self.__LOADING_DOTS_X_COORDS = [932, 959, 985]
        self.__GREEN_RANGE = self.__validateColourRange(greenRange)
        self.__ORANGE_RANGE = self.__validateColourRange(orangeRange)
        self.__DESLOT_THRESHOLD = deslotThreshold
        self.__SAMPLE_ITERATIONS = sampleIters
        
        # initializing OpenCV objects
        self.__cameraFeed = cv.VideoCapture(1)
        self.__backgroundSubtractor = cv.createBackgroundSubtractorMOG2(detectShadows=False)
        self.__detector = cv.SimpleBlobDetector_create()
        
        self.__cameraIsWorking = True
        self.__trackLocations = {}
        
        # validating parameters
        if self.__GREEN_RANGE == [] or self.__ORANGE_RANGE == []:
            raise ValueError("Invalid colour range passed in")
        
        measurementFrame = self.__readFrame()
        if self.__cameraIsWorking:
            self.__IMAGE_WIDTH = measurementFrame.shape[1]
            self.__IMAGE_HEIGHT = measurementFrame.shape[0]
        else:
            self.__IMAGE_WIDTH = 1920
            self.__IMAGE_HEIGHT = 1080
            
# ==================== Private Methods ========================================    
        
    def __readFrame(self):
        successful, frame = self.__cameraFeed.read()
        if successful:
            return frame
        else:
            print("Frame could not be read: __readFrame")
            self.__cameraIsWorking = False
            return None
        
        
    @staticmethod
    def __validateColourRange(colourRange: list) -> list:
        if len(colourRange) != 2:
            return []
        for i, bound in enumerate(colourRange):
            for j, colourVal in enumerate(bound):
                try:
                    val = int(colourVal)
                    if val >= 0 and val <= 255: #BGR colours: 0-255
                        colourRange[i][j] = val
                    else:
                        raise ValueError
                except ValueError:
                    print(colourVal, "is not a valid colour")
                    return []
        return np.array(colourRange)
    
    
    def __getCarLocation(self, zoomDepth=0, zoomPerc=0) -> tuple:    
        if not self.__cameraIsWorking:
            return -1, -1
        
        frame = self.__readFrame()
        foreGroundMask = self.__backgroundSubtractor.apply(frame)
        foreGroundMask = cv.blur(foreGroundMask, (5,5))
        meanX, meanY = self.__CalcAverageLocation(foreGroundMask)
        size = self.__IMAGE_WIDTH
        for _ in range(zoomDepth):
            size = int(size*zoomPerc)
                
            newForeGround, x1, y1 = self.__getZoomedMask(foreGroundMask, meanX, meanY, size) # Try: should this not be newForeGround????
            meanX, meanY = self.__CalcAverageLocation(newForeGround)
            meanX += x1
            meanY += y1
            
        return meanX, meanY
    
    def __getZoomedMask(self, curMask, meanX: int, meanY: int, size: int) -> tuple:
        x1 = meanX-size if meanX-size >= 0 else 0
        y1 = meanY-size if meanY-size >= 0 else 0
        x2 = meanX+size if meanX+size <= self.__IMAGE_WIDTH else self.__IMAGE_WIDTH
        y2 = meanY+size if meanY+size <= self.__IMAGE_HEIGHT else self.__IMAGE_HEIGHT
        return curMask[y1:y2, x1:x2], x1, y1
        
    def __CalcAverageLocation(self, mask) -> tuple:
        maskPositiveCoords = np.where(mask == 255)
        xCoords = maskPositiveCoords[1]
        yCoords = maskPositiveCoords[0]
        
        if len(xCoords) > 0:
            meanX = int(np.mean(xCoords))
            meanY = int(np.mean(yCoords))
            return meanX, meanY
        else:
            print("NaN Error Received, check zoom parameters")
        return -1, -1
    
    def __gatherSampleFrames(self):
        sampleFrames = []
        for _ in range(self.__SAMPLE_ITERATIONS):
            if self.__cameraIsWorking:
                frame = self.__readFrame()
                sampleFrames.append(frame)
            else:
                print("Search failed due to camera failing: __gatherSampleFrames")
                return []
        return sampleFrames


# ==================== Public Methods ========================================

    def trainBackgroundOnFrames(self, frames):
        for frame in frames:
            self.__backgroundSubtractor.apply(frame)

        
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
        
        if sum(results) > 1: # majority of frames have no dots
            self.__cameraIsWorking = True
            return True
        else:
            self.__cameraIsWorking = False
            return False
        
    def FindTrackLocationsInFrames(self, frames, targetNum):
        locationsFound = {}
        for frame in frames:
            greenMask = cv.inRange(frame, *self.__GREEN_RANGE)
            greenMask = cv.bitwise_not(cv.blur(greenMask, (15,15)))
            orangeMask = cv.inRange(frame, *self.__ORANGE_RANGE)
            orangeMask = cv.bitwise_not(cv.blur(orangeMask, (15,15)))
            
            greenLocations = self.__detector.detect(greenMask)
            orangeLocations = self.__detector.detect(orangeMask)
            
            for loc in greenLocations: #improve
                x,y = loc.pt
                locationsFound[(x,y)] = self.__GREEN
                
            for loc in orangeLocations:
                x,y = loc.pt
                locationsFound[(x,y)] = self.__ORANGE
                
            if len(locationsFound) == targetNum:
                print("all locations found")
                return locationsFound # break out of loop
            
            locationsFound = {}
            
        print("not all track locations were found, please calibrate colours")
        return locationsFound 
    
    def checkCarAndTrackLocationsFound(self, targetNumTrackLocations):
        # gather frames
        sampleFrames = self.__gatherSampleFrames()
        
        # use frames to find possible car
        self.trainBackgroundOnFrames(sampleFrames)
        carFound = (self.__getCarLocation() != (-1,-1))
        
        # use the same frames to find the track locations: no need to read more frames (faster)
        self.__trackLocations = self.FindTrackLocationsInFrames(sampleFrames, targetNumTrackLocations)
        return carFound, len(self.__trackLocations)

    
        
if __name__ == '__main__':
    green = [[80, 180, 160], [120, 255, 220]]
    orange = [[50, 110, 200], [90, 190, 255]]
    try:
        cam = CameraInput(green,
                          orange,
                          0, 50)
    except ValueError:
        print("invalid")
    print(cam.checkCameraIsConnected())
    print(cam.checkCarAndTrackLocationsFound(6))
            
            
            
   # def showAFrame(self):
    #     while True:
    #         cv.imshow("Test Frame", self.__readFrame())
    #         key = cv.waitKey(1)
    #         if key == 27:
    #             break 