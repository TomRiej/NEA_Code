from Constants import *

import cv2 as cv
import numpy as np
from time import time
from math import sqrt
from heapq import nsmallest

class CameraInput:
    def __init__(self) -> None:
        self.__GREEN_RANGE = self.__validateColourRange(GREEN_RANGE)
        self.__ORANGE_RANGE = self.__validateColourRange(ORANGE_RANGE)
        self.__BLUE_RANGE = self.__validateColourRange(BLUE_RANGE)
        
        self.__GREEN = 0
        self.__ORANGE = 1
        
        self.__cameraFeed = cv.VideoCapture(1)
        self.__backgroundSubtractor = cv.createBackgroundSubtractorMOG2(detectShadows=False)
        self.__detector = cv.SimpleBlobDetector_create()
        
        self.__trackLocations = {}
        
        success, measurementFrame = self.__cameraFeed.read()
        if success:
            self.__IMAGE_WIDTH = measurementFrame.shape[1]
            self.__IMAGE_HEIGHT = measurementFrame.shape[0]
        else:
            raise ValueError("Camera", "Could not use camera feed to read a frame")
        
        
# ==================== General ========================================
    @staticmethod  
    def __validateColourRange(colourRange: list) -> np.array:
        """validates all the colour values in the range to be integers between 0 and 255.

        Args:
            colourRange (list): the 2D list with the BRG colour values

        Raises:
            ValueError: when the colour range doesn't have a length of 2 (list for lower and upper)
            ValueError: when a colour value is not an integer
            ValueError: when a colour value is not between 0-255
        Error raised should be handled by the script importing this one

        Returns:
            np.array: a numpy array with data type unsigned integer (8bits) to hold values between
                      0-255 which is perfect for BGR colour values
        """
        if len(colourRange) != 2:
            raise ValueError("Camera", f"ColourRange: {colourRange} doesn't have length 2")
        for bound in colourRange: 
            for colourValue in bound:
                try:
                    colourValue = int(colourValue)
                except ValueError:
                    raise ValueError("Camera", f"ColourValue: {colourValue} in "+
                                               f"colourRange: {colourRange} is not an integer")
                if not 0 <= colourValue <= 255:
                    raise ValueError("Camera", f"ColourValue: {colourValue} in "+
                                               f"colourRange: {colourRange} is "+
                                                "not between 0 -> 255")
        # uint8 uses 8 bits to store integer from 0->255: perfect for BGR colour values
        return np.array(colourRange, dtype="uint8")
    
    
# ==================== Validation Routine ========================================
    def __gatherSampleFrames(self) -> list:
        frames = []
        for _ in range(SAMPLE_ITERATIONS):
            success, frame = self.__cameraFeed.read()
            if not success:
                return INVALID
            frames.append(frame)
        return frames
    
    def __trainBackground(self, trainingFrames: list) -> None:
        for frame in trainingFrames:
            self.__backgroundSubtractor.apply(frame)
    
    def __getAverageNumCarPixels(self, sampleFrames: list) -> int:
        totalPixels = 0
        for frame in sampleFrames:
            foregroundMask = self.__backgroundSubtractor.apply(frame)
            foregroundMask = cv.blur(foregroundMask, (5, 5))
            totalPixels += len(np.where(foregroundMask == 255))
        
        # prevent division by 0 error
        if len(sampleFrames) > 0:
            return totalPixels // len(sampleFrames)
        else:
            return 0
    
    def __findAndSaveTrackLocations(self, sampleFrames: list) -> int:
        for frame in sampleFrames:
            locationsFound = {}
            
            # generate masks for both green and orange
            greenMask = cv.inRange(frame, *self.__GREEN_RANGE)
            greenMask = cv.bitwise_not(cv.blur(greenMask, (15,15)))
            orangeMask = cv.inRange(frame, *self.__ORANGE_RANGE)
            orangeMask = cv.bitwise_not(cv.blur(orangeMask, (15,15)))
            
            # detect blobs and save their (x, y) coords in a dictionary
            for loc in self.__detector.detect(greenMask):
                locationsFound[(int(loc.pt[0]), int(loc.pt[1]))] = self.__GREEN
                
            for loc in self.__detector.detect(orangeMask):
                locationsFound[(int(loc.pt[0]), int(loc.pt[1]))] = self.__ORANGE
                
            # save and break out the loop if we've found them all    
            if len(locationsFound) == NUM_TRACK_LOCATIONS:
                self.__trackLocations = locationsFound
                break
        
        # incase 0 frames are passed in and this raises an error for undefined locationsFound
        if len(sampleFrames) > 0: 
            return len(locationsFound)
        else:
            return 0
        
    def checkCameraConnected(self) -> bool:
        """Checks if the camera is actually sending the live video feed to me. 
        If the camera is not connected, a screen with 3 blue loading dots is shown instead. 
        This method checks if those blue dots are present. if yes, then the camera is not connected
        and the method should return False.
        
        Returns:
            bool: True if blue dots can't be found, meaning the camera feed is connected.
        """
        resultForEachFrame = []
        for _ in range(3):
            success, frame = self.__cameraFeed.read()
            if not success:
                resultForEachFrame.append(False)
                
            blueMask = cv.inRange(frame, *self.__BLUE_RANGE)
            blueMask = cv.bitwise_not(cv.blur(blueMask, (5,5)))
            blueBlobsXCoords = sorted([int(dot.pt[0]) for dot in self.__detector.detect(blueMask)])
            if blueBlobsXCoords == LOADING_DOTS_X_COORDS:
                resultForEachFrame.append(False)
            else:
                resultForEachFrame.append(True)
        
        return sum(resultForEachFrame) > 1
    
    def countCarPixelsAndTrackLocations(self) -> tuple:
        # gather sample frames
        sampleFrames = self.__gatherSampleFrames()
        if sampleFrames is INVALID:
            return 0, 0
        
        # count car pixels
        self.__trainBackground(sampleFrames)
        averageNumCarPixels = self.__getAverageNumCarPixels(sampleFrames)
        
        # use the same frames to find track locations so I dont waste time getting more frames
        numTrackLocations = self.__findAndSaveTrackLocations(sampleFrames)
        
        return averageNumCarPixels, numTrackLocations
        

# ==================== Training ========================================
    def __calcAverageLocation(mask: np.array) -> tuple: # TEST
        xCoords, yCoords = np.where(mask == 255)
        
        if len(xCoords) > 0:
            return int(np.mean(xCoords)), int(np.mean(yCoords))
        else:
            return INVALID

    def __getCarLocation(self) -> tuple:
        # get measurement frame and time of measurement
        success, frame = self.__cameraFeed.read()
        timeOfMeasurement = time()
        if not success:
            return INVALID, INVALID
        
        # generate mask
        foreGroundMask = self.__backgroundSubtractor.apply(frame)
        foreGroundMask = cv.blur(foreGroundMask, (5,5))
        
        # find car in mask
        return self.__calcAverageLocation(foreGroundMask), timeOfMeasurement
        
    def __pixelsToMillimeters(self, distancePixels: float) -> float:
        return distancePixels * MILLIMETERS_PER_PIXEL
    
    def __calcDistanceMillimeters(self, startCoords: tuple, endCoords: tuple) -> float:
        xDistancePixels = endCoords[0] - startCoords[0]
        yDistancePixels = endCoords[1] - startCoords[1]
        distancePixels = sqrt((xDistancePixels**2) + (yDistancePixels**2))
        return self.__pixelsToMillimeters(distancePixels)
            
    def __getCarSpeed(self, startCoords: tuple, endCoords: tuple, timeSeconds: float) -> float:
        distanceMillimeters = self.__calcDistanceMillimeters(startCoords, endCoords)
        return distanceMillimeters / timeSeconds
        
    def __getNextTrackLocationInfo(startCoords: tuple, endCoords: tuple) -> tuple:
        pass         
            
                
    def getCarInfo(self):
        info = {}
        startCoords, startTime = self.__getCarLocation()
        if startCoords is INVALID:
            return INVALID
        
        endCoords, endTime = self.__getCarLocation()
        if endCoords is INVALID:
            return INVALID
        
        ellapsedTimeSeconds = endTime - startTime
        
        info["location"] = endCoords
        info["speed"] = self.__getCarSpeed(startCoords, endCoords, ellapsedTimeSeconds)
        info["timeOfMeasurement"] = endTime
        
        
        
        
if __name__ == '__main__':
    c = CameraInput()