import cv2 as cv
import numpy as np
from time import time
from math import sqrt
from heapq import nsmallest


class CameraInput:
    def __init__(self, greenRange: list, orangeRange: list) -> None:
        # initializing OpenCV objects
        self.__cameraFeed = cv.VideoCapture(1)
        self.__backgroundSubtractor = cv.createBackgroundSubtractorMOG2(detectShadows=False)
        self.__detector = cv.SimpleBlobDetector_create()
        
        # getting image dimensions
        self.__readFailure = True
        frame = self.__readFrame()
        if self.__readFailure: # frame needs to be read to get img size
            print("Camera module not created")
            return None
        imgShape = frame.shape
        self.__width = imgShape[1]
        self.__height = imgShape[0]
        
        # getting colour ranges
        self.__greenRange = self.__validateColourRange(greenRange)
        self.__orangeRange = self.__validateColourRange(orangeRange)
        if self.__greenRange == [] or self.__orangeRange == []:
            print("invalid colour range")
            return None
        else:
            self.__greenRange = np.array(self.__greenRange)
            self.__orangeRange = np.array(self.__orangeRange)
        
        # initializing empty Track locations
        self.__trackLocations = {}
        self.__GREEN = 0
        self.__ORANGE = 1
        self.__DESLOT_THRESHOLD = 0
        
    # =============== Private Methods =============================        
        
    def __readFrame(self):
        successful, frame = self.__cameraFeed.read()
        if not successful:
            self.__readFailure = True
            print("frame could not be read")
            return None
        else:
            self.__readFailure = False
            return frame
    
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
        return colourRange
    
    def __getCarLocation(self, zoomDepth: int, zoomPerc: float) -> tuple:    
        frame = self.__readFrame()
        if self.__readFailure:
            return None, None
        
        foreGroundMask = self.__backgroundSubtractor.apply(frame)
        foreGroundMask = cv.blur(foreGroundMask, (5,5))
        meanX, meanY = self.__CalcAverageLocation(foreGroundMask)
        size = self.__width
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
        x2 = meanX+size if meanX+size <= self.__width else self.__width
        y2 = meanY+size if meanY+size <= self.__height else self.__height
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
    
    def __getDistBetweenCoords(self, p1: tuple, p2: tuple) -> float:
        xDist = p2[0] - p1[0]
        yDist = p2[1] - p1[1] # very annoying bug here was p2[1]
        pixelDist = sqrt((xDist**2) + (yDist**2))
        return self.__pixelToDist(pixelDist)
    
    def __pixelToDist(self, distance: float) -> float:
        k = 200 / 1445 # 200cm takes up 1445 pixels: known from calibration
        return distance*k
    
    def __getCarSpeed(self, startCoords: tuple, endCoords: tuple, time: float) -> float:
        distance = self.__getDistBetweenCoords(startCoords, endCoords)
        return distance / time
    
              
    # ================= Public Methods ==========================
    
    def updateTrackLocations(self, numToFind: int, maxIters: int) -> bool:
        for _ in range(maxIters):
            numLocsFound = 0
            self.__trackLocations = {}
            frame = self.__readFrame()
            if self.__readFailure:
                print("track locations not updated")
                return False
            
            greenMask = cv.inRange(frame, *self.__greenRange)
            greenMask = cv.bitwise_not(cv.blur(greenMask, (15,15)))
            orangeMask = cv.inRange(frame, *self.__orangeRange)
            orangeMask = cv.bitwise_not(cv.blur(orangeMask, (15,15)))
            
            greenKeyPoints = self.__detector.detect(greenMask)
            orangeKeyPoints = self.__detector.detect(orangeMask)
            
            for object in greenKeyPoints: # green is 0
                x = int(object.pt[0])
                y = int(object.pt[1])
                self.__trackLocations[(x,y)] = self.__GREEN
                numLocsFound += 1
                
            for object in orangeKeyPoints: # orange is 1
                x = int(object.pt[0])
                y = int(object.pt[1])
                self.__trackLocations[(x,y)] = self.__ORANGE
                numLocsFound += 1
                
            if numLocsFound == numToFind:
                print("all locations found and saved")
                print(self.__trackLocations)
                return True
        
        print("Max iterations reached:")
        if numLocsFound > numToFind:
            print("Too many locations found")
        else:
            print("Too little locations found")
        print(self.__trackLocations)
        print("Please calibrate the colours")       
        return False
        
        
    def trainBackground(self, numFrames:int) -> bool:
        for _ in range(numFrames):
            frame = self.__readFrame()
            if self.__readFailure:
                print("Failed to train background")
                return False
            else:
                self.__backgroundSubtractor.apply(frame)
                
        print("Training complete")
        return True
        
        
    def getCarInfo(self, zD: int, zP: float) -> dict:
        info = {}
        startTime = time()
        startCoords = self.__getCarLocation(zD,zP)
        endCoords = self.__getCarLocation(zD,zP)
        endTime = time()
        elapsedTime = endTime-startTime
        
        info["carLocation"] = endCoords
        info["carSpeed"] = self.__getCarSpeed(startCoords, endCoords, elapsedTime)
        info["nextTrackLoc"] = self.getNextTrackLocation(startCoords, endCoords)
        info["nextTrackLocDist"] = self.__getDistBetweenCoords(endCoords, info["nextTrackLoc"])
        info["nextTrackLocType"] = self.__trackLocations[info["nextTrackLoc"]]
        if info["carSpeed"] <= self.__DESLOT_THRESHOLD:
            info["deslotted"] = True
        else:
            info["deslotted"] = False
        
        return info
        
    def getNextTrackLocation(self, carLoc1: tuple, carLoc2: tuple) -> tuple:
        locDistances = {}
        for loc in self.__trackLocations:
            dist = self.__getDistBetweenCoords(carLoc1, loc)
            locDistances[loc] = dist
        
        
        loc1, loc2 = nsmallest(2, locDistances, key=locDistances.get)
        newLoc1Dist = self.__getDistBetweenCoords(carLoc2, loc1)
        newLoc2Dist = self.__getDistBetweenCoords(carLoc2, loc2)
        deltaDist1 = newLoc1Dist - locDistances[loc1]
        deltaDist2 = newLoc2Dist - locDistances[loc2]
        if deltaDist1 < deltaDist2:
            return loc1 
        else:
            return loc2
        
    def test(self):
        while True:
            frame = self.__readFrame()
            info = self.getCarInfo(0,0.1)
            cv.circle(frame, (info["carLocation"]), 50, (0, 255, 0), 3)
            cv.circle(frame, (info["nextTrackLoc"]), 50, (255, 255, 255), 3)
            
            if info["deslotted"]:
                cv.circle(frame, (info["carLocation"]), 50, (0,0,255), 3)
            
            cv.imshow("f", frame)
            
            key = cv.waitKey(1)
            if key == 27:
                print("The returned info looks like:")  
                print(info)
                break  
   
# # Test 1
# badRange1 = [[0, -1, 255],[300, 45, 6]]   
# badRange2 = [["four", "56", "34"], ["255", "3", "35"]]   
# errorCam = CameraInput(badRange1, badRange2)
# Test 2
greenRange = [[70, 200, 180], [110, 255, 220]]
orangeRange = [[40, 140, 210], [70, 180, 255]]
cam = CameraInput(greenRange, orangeRange)
success = cam.updateTrackLocations(6, 50)
if success:
    timeStart = time()
    cam.trainBackground(50)
    cam.test()
    # count = 0
    # while time()-timeStart < 10:
    #     count += 1
    #     info = cam.getCarInfo(1,0.1)
    # print(count)
    
    # cam.test()