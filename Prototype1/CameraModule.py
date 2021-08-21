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
BGR_YELLOW = (0,242,255)
BGR_GREEN = (0,255,0)
BGR_ORANGE = (0,162,255)


class CameraInput:
    def __init__(self, greenRange, orangeRange, deslotThreshold, sampleIters, MillimetersPerPixel):
        # Initializing constants
        self.__GREEN = 0
        self.__ORANGE = 1
        self.__BLUE = np.array([254, 81, 20], dtype=np.uint8)
        self.__LOADING_DOTS_X_COORDS = [932, 959, 985]
        self.__GREEN_RANGE = self.__validateColourRange(greenRange)
        self.__ORANGE_RANGE = self.__validateColourRange(orangeRange)
        self.__DESLOT_THRESHOLD = deslotThreshold
        self.__SAMPLE_ITERATIONS = sampleIters
        self.__MILLIMETERS_PER_PIXEL = MillimetersPerPixel
        
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
# ==================== General
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
    
    
# ==================== Validation 
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
    
    
    def __trainBackgroundOnFrames(self, frames):
        for frame in frames:
            self.__backgroundSubtractor.apply(frame)
    
    
    def __findTrackLocationsInFrames(self, frames, targetNum):
        locationsFound = {}
        for frame in frames:
            locationsFound = {}
            greenMask = cv.inRange(frame, *self.__GREEN_RANGE)
            greenMask = cv.bitwise_not(cv.blur(greenMask, (15,15)))
            orangeMask = cv.inRange(frame, *self.__ORANGE_RANGE)
            orangeMask = cv.bitwise_not(cv.blur(orangeMask, (15,15)))
            
            greenLocations = self.__detector.detect(greenMask)
            orangeLocations = self.__detector.detect(orangeMask)
            
            for loc in greenLocations: #improve
                x,y = int(loc.pt[0]), int(loc.pt[1])
                locationsFound[(x,y)] = self.__GREEN
                
            for loc in orangeLocations:
                x,y = int(loc.pt[0]), int(loc.pt[1])
                locationsFound[(x,y)] = self.__ORANGE
                
            if len(locationsFound) == targetNum:
                return locationsFound # break out of loop
                
        print("not all track locations were found, please calibrate colours")
        return locationsFound
    

    def __getNumCarPixelsInFrames(self, frames):
        numPixelsPerFrame = []
        for frame in frames:
            foreGroundMask = self.__backgroundSubtractor.apply(frame)
            foreGroundMask = cv.blur(foreGroundMask, (5,5))
            maskPositiveCoords = np.where(foreGroundMask == 255)
            numPixelsPerFrame.append(len(maskPositiveCoords[0]))
        return np.mean(numPixelsPerFrame)


# ==================== Training   
    def __getCarLocation(self, zoomDepth, zoomPerc) -> tuple:    
        if not self.__cameraIsWorking:
            return (-1, -1), -1
        
        frame = self.__readFrame()
        timestamp = time()
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
            
        return (meanX, meanY), timestamp
    
    def __getZoomedMask(self, curMask, meanX: int, meanY: int, size: int) -> tuple:
        x1 = meanX-size if meanX-size >= 0 else 0
        y1 = meanY-size if meanY-size >= 0 else 0
        x2 = meanX+size if meanX+size <= self.__IMAGE_WIDTH else self.__IMAGE_WIDTH
        y2 = meanY+size if meanY+size <= self.__IMAGE_HEIGHT else self.__IMAGE_HEIGHT
        return curMask[y1:y2, x1:x2], x1, y1
        
    def __CalcAverageLocation(self, mask) -> tuple:
        maskPositiveCoords = np.where(mask == 255)
        # print(len(maskPositiveCoords[0]), end=", ")
        xCoords = maskPositiveCoords[1]
        yCoords = maskPositiveCoords[0]
        
        if len(xCoords) > 0:
            meanX = int(np.mean(xCoords))
            meanY = int(np.mean(yCoords))
            return meanX, meanY
        else:
            print("NaN Error Received, check zoom parameters")
        return -1, -1
    
    def __getCarSpeed(self, startCoords, endCoords, secondsTimeTaken):
        millimeterDistance = self.__getMillimetersBetweenCoords(startCoords, endCoords)
        return millimeterDistance / secondsTimeTaken
        
    def __getNextTrackLocation(self, startCoords, endCoords):
        # get the distance from the car from each track location
        locDistances = {}
        for loc in self.__trackLocations:
            dist = self.__getMillimetersBetweenCoords(startCoords, loc)
            locDistances[loc] = dist
            
        # get the 2 closest locations
        loc1, loc2 = nsmallest(2, locDistances, key=locDistances.get)
        
        # check which location has their distance decreasing (next location)
        newLoc1Dist = self.__getMillimetersBetweenCoords(endCoords, loc1)
        newLoc2Dist = self.__getMillimetersBetweenCoords(endCoords, loc2)
        deltaDist1 = newLoc1Dist - locDistances[loc1]
        deltaDist2 = newLoc2Dist - locDistances[loc2]
        if deltaDist1 < deltaDist2:
            return loc1, newLoc1Dist 
        else:
            return loc2, newLoc2Dist
        
        
    
    def __getMillimetersBetweenCoords(self, p1, p2):
        xDist = p2[0] - p1[0]
        yDist = p2[1] - p1[1] 
        pixelDist = sqrt((xDist**2) + (yDist**2))
        return self.__pixelToMilimeter(pixelDist)
    
    def __pixelToMilimeter(self, pixelDistance):
        return pixelDistance * self.__MILLIMETERS_PER_PIXEL
    
    
# ==================== Public Methods ========================================
# ==================== General
    def close(self):
        self.__cameraFeed.release()


# ==================== Validation         
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
        
     
    def checkCarAndTrackLocationsFound(self, targetNumTrackLocations):
        # gather frames
        sampleFrames = self.__gatherSampleFrames()
        
        # use frames to find possible car
        self.__trainBackgroundOnFrames(sampleFrames)
        averageNumCarPixels = self.__getNumCarPixelsInFrames(sampleFrames)
        
        # use the same frames to find the track locations: no need to read more frames (faster)
        self.__trackLocations = self.__findTrackLocationsInFrames(sampleFrames, targetNumTrackLocations)
        return averageNumCarPixels, len(self.__trackLocations)
    
    
# ==================== Training  
    def getCarInfo(self, zD: int, zP: float) -> dict:
        info = {}
        startCoords, startTime = self.__getCarLocation(zD,zP)
        endCoords, endTime = self.__getCarLocation(zD,zP)
        elapsedTime = endTime-startTime
        
        info["carLocation"] = endCoords
        info["carSpeed"] = self.__getCarSpeed(startCoords, endCoords, elapsedTime) # mm / s
        info["nextTrackLoc"], info["nextTrackLocDist"] = self.__getNextTrackLocation(startCoords, endCoords) # (x,y), mm
        info["nextTrackLocType"] = self.__trackLocations[info["nextTrackLoc"]]
        if info["carSpeed"] <= self.__DESLOT_THRESHOLD:
            info["deslotted"] = True
        else:
            info["deslotted"] = False
        
        return info
    
    # def test(self):
    #     for i in range(100):
    #         self.__getCarLocation()
    
    # def showTestFrames(self):
    #     if self.__cameraIsWorking:
    #         while True:
    #             frame = self.__readFrame()
    #             carLocation = self.__getCarLocation()
                
    #             for loc in self.__trackLocations.keys():
    #                 if self.__trackLocations[loc]:
    #                     cv.circle(frame, loc, 50, BGR_ORANGE, 3)
    #                 else:
    #                     cv.circle(frame, loc, 50, BGR_GREEN, 3)
    #             cv.circle(frame, carLocation, 50, BGR_YELLOW, 3)
                
            
    #             cv.imshow("test frame", frame)
    #             k = cv.waitKey(1)
    #             if k == 27:
    #                 break
        
        
                
                
    


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
    # cam.test()
    # cam.showTestFrames()
            
            
            
   # def showAFrame(self):
    #     while True:
    #         cv.imshow("Test Frame", self.__readFrame())
    #         key = cv.waitKey(1)
    #         if key == 27:
    #             break 
    
    # from random import randint
    # b = [3000, 6000]
    # for i in range(10000000):
    #     n = randint(0, 10000)
    #     if n in range(*b): # ~ 23s
    #     # b[0] <= n <= b[1]: ~19s
    #         pass
    
    
