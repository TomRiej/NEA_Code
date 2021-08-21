import cv2 as cv
import numpy as np
import time
from math import sqrt

DEBUG = False

class CameraInput:
    def __init__(self):
        self.__cameraFeed = cv.VideoCapture(1)
        self.__backgroundSubractor = cv.createBackgroundSubtractorMOG2(detectShadows=False)
        
        self.__readFailure = True
        frame = self.__readFrame()
        if self.__readFailure:
            print("Camera module not created")
            return None
        imgShape = frame.shape
        self.__width = imgShape[1]
        self.__height = imgShape[0]
        
        if DEBUG:
            print(f"width: {self.__width}  height: {self.__height}")
        
        
    def __readFrame(self):
        successful, frame = self.__cameraFeed.read()
        if not successful:
            self.__readFailure = True
            print("frame could not be read")
            return None
        else:
            self.__readFailure = False
            return frame
        
        
    def trainBackground(self, numFrames):
        for _ in range(numFrames):
            frame = self.__readFrame()
            if self.__readFailure:
                print("Failed to train background")
                return False
            else:
                self.__backgroundSubractor.apply(frame)
                
        print("Training complete")
        return True
        
    def getCarSpeed(self, zD: int, zP: float) -> float:
        startTime = time.time()
        startCoords = self.getCarLocation(zD,zP)
        endCoords = self.getCarLocation(zD,zP)
        endTime = time.time()
        distance = self.__getDistBetweenCoords(startCoords, endCoords)
        speed = distance / (endTime-startTime)
        return startCoords, endCoords, speed
        
    def __getDistBetweenCoords(self, p1: tuple, p2: tuple) -> float:
        xDist = p2[0] - p1[0]
        yDist = p2[1] - p2[1]
        pixelDist = sqrt((xDist**2) + (yDist**2))
        return self.__pixelToDist(pixelDist)
    
    def __pixelToDist(self, distance: float) -> float:
        k = 2000 / self.__width
        return distance*k
        
        
    def showCarLocation(self, zoomDepth: int, zoomPerc: float) -> None: # for seeing the output
        while True:
            frame = self.__readFrame()
            if self.__readFailure:
                return None
            
            foreGroundMask = self.__backgroundSubractor.apply(frame)
            
            foreGroundMask = cv.blur(foreGroundMask, (5,5))
            meanX, meanY = self.__CalcAverageLocation(foreGroundMask)
            # original mean: (red circle)
            cv.circle(frame, (meanX, meanY), 50, (0,0,255), 3)
            size = self.__width
            for _ in range(zoomDepth):
                size = int(size*zoomPerc)
                    
                newForeGround, x1, y1, x2, y2 = self.__getZoomedMask(foreGroundMask, meanX, meanY, size)
                meanX, meanY = self.__CalcAverageLocation(newForeGround)
                meanX += x1
                meanY += y1
            
            # final region: (white box)
            cv.rectangle(frame, (x1,y1), (x2,y2), (255,255,255), 3)
            # final mean: (green circle)
            cv.circle(frame, (meanX, meanY), 50, (0,255,0), 3 )

            # cv.circle(frame, (meanX, meanY), 50, (0,0,255), 3)
            # cv.circle(frame, (meanX2, meanY2), 50, (0,255,0), 3)
            
            cv.imshow("mask", foreGroundMask)
            # cv.imshow("newMask", newForeGround)
            cv.imshow("Output", frame)
                
            key = cv.waitKey(1)
            if key == 27:
                break
            
    def __getZoomedMask(self, curMask, meanX: int, meanY: int, size: int) -> tuple:
        x1 = meanX-size if meanX-size >= 0 else 0
        y1 = meanY-size if meanY-size >= 0 else 0
        x2 = meanX+size if meanX+size <= self.__width else self.__width
        y2 = meanY+size if meanY+size <= self.__height else self.__height
        return curMask[y1:y2, x1:x2], x1, y1, x2, y2
        
    
    def __CalcAverageLocation(self, mask):
        maskPositiveCoords = np.where(mask == 255)
        xCoords = maskPositiveCoords[1]
        yCoords = maskPositiveCoords[0]
        
        if len(xCoords) > 0:
            meanX = int(np.mean(xCoords))
            meanY = int(np.mean(yCoords))
            return meanX, meanY
        else:
            print("NaN Error Received, check zoom perc parameters")
        return -1,-1
    
    def getCarLocation(self, zoomDepth: int, zoomPerc: float) -> tuple:    
        frame = self.__readFrame()
        if self.__readFailure:
            return None, None
        
        foreGroundMask = self.__backgroundSubractor.apply(frame)
        
        meanX, meanY = self.__CalcAverageLocation(foreGroundMask)
        size = self.__width
        for _ in range(zoomDepth):
            size = int(size*zoomPerc)
                
            newForeGround, x1, y1, x2, y2 = self.__getZoomedMask(foreGroundMask, meanX, meanY, size)
            meanX, meanY = self.__CalcAverageLocation(newForeGround)
            meanX += x1
            meanY += y1
            
        return meanX, meanY
    
    def draw(self, locations):
        frame = self.__readFrame()
        for x,y in locations:
            cv.circle(frame, (x,y), 10, (0,255,0))
        while True:
            cv.imshow("frame", frame)
            
            key = cv.waitKey(1)
            if key == 27:
                break
            


if __name__ == '__main__':
    cam = CameraInput()
    trained = cam.trainBackground(50)
    locations = []
    if trained:
        cam.showCarLocation(1, 0.05)
        # for i in range(10):
        #     # meanX, meanY = cam.getCarLocation(4, 0.5)
        #     start, end, spd = cam.getCarSpeed(4, 0.5)
        #     print(f"from {start} to {end} spd: {spd}")
        #     locations.append(start)
        #     locations.append(end)
            
    else:
        print("not trained")
    # print(locations)
    # cam.draw(locations)
    
    
    