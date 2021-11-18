from Constants import *

import cv2 as cv
import numpy as np
from time import time
from math import sqrt
from heapq import nsmallest


class CameraInput:
    def __init__(self) -> None:
        """Constructor for the camera module. It validates the colour ranges and the number of 
        track locations. It also initialises the background subtractor and blob detector.

        Raises:
            ValueError: if the number of track locations is fewer than two
        """
        # redefine as they are converted to np arrays
        self.__GREEN_RANGE = self.__validateColourRange(GREEN_RANGE)
        self.__ORANGE_RANGE = self.__validateColourRange(ORANGE_RANGE)
        self.__BLUE_RANGE = self.__validateColourRange(BLUE_RANGE)
        
        if NUM_TRACK_LOCATIONS < 2:
            raise ValueError("Camera", "The number of track locations must be at least 2")
        
        self.__cameraFeed = cv.VideoCapture(1)
        self.__backgroundSubtractor = cv.createBackgroundSubtractorMOG2(detectShadows=False)
        self.__detector = cv.SimpleBlobDetector_create()
        
        self.__trackLocations = {}
        
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
            raise ValueError("Camera", f"ColourRange: '{colourRange}' doesn't have length 2")
        for bound in colourRange: 
            for colourValue in bound:
                try:
                    colourValue = int(colourValue)
                except ValueError:
                    raise ValueError("Camera", f"ColourValue: '{colourValue}' in "+
                                               f"colourRange: '{colourRange}' is not an integer")
                if not 0 <= colourValue <= 255:
                    raise ValueError("Camera", f"ColourValue: '{colourValue}' in "+
                                               f"colourRange: '{colourRange}' is "+
                                                "not between 0 -> 255")
        # uint8 uses 8 bits to store integer from 0->255: perfect for BGR colour values
        return np.array(colourRange, dtype="uint8")
    
    def close(self) -> None:
        """correct way to close the camera input.
        """
        self.__cameraFeed.release()
        
        
# ==================== Validation Routine ========================================
    def __gatherSampleFrames(self) -> list:
        """a method that will take SAMPLE_ITERATIONS number of frames from the camera and 
        return them as a list. If there is an issue with gathering frames, it return INVALID

        Returns:
            list: the collection of frames gathered
        """
        frames = []
        for _ in range(SAMPLE_ITERATIONS):
            success, frame = self.__cameraFeed.read()
            if not success:
                return INVALID
            frames.append(frame)
        return frames
    
    def __trainBackground(self, trainingFrames: list) -> None:
        """trains the background subtractor module on the list of camera frames passed in.

        Args:
            trainingFrames (list): a collection of SAMPLE_ITERATIONS frames from the camera
        """
        for frame in trainingFrames:
            self.__backgroundSubtractor.apply(frame)
    
    def __getAverageNumCarPixels(self, sampleFrames: list) -> int:
        """calculates the average number of moving pixels in the sampleFrames, which can later
        be used to validate if the car is seen.
        

        Args:
            sampleFrames (list): a list of frames from the camera

        Returns:
            int: returns a value for the mean number of pixels as an integer.
        """
        totalPixels = 0
        for frame in sampleFrames:
            foregroundMask = self.__backgroundSubtractor.apply(frame)
            foregroundMask = cv.blur(foregroundMask, (5, 5))
            # we need to index '[0]' as np.where returns list format: [[all,the,xs], [all,the,ys]]
            # len([all,the,xs]) will be the number of moving pixels.
            # positive pixels are represented with value 255 which is white.
            totalPixels += len(np.where(foregroundMask == 255)[0])
        
        # prevent division by 0 error
        if len(sampleFrames) > 0:
            return totalPixels // len(sampleFrames)
        else:
            return 0
    
    def __findAndSaveTrackLocations(self, sampleFrames: list) -> int:
        """uses a blob detector and the defined colour ranges to try find all the track locations
        in the sample frames. If they're all found, they are saved.

        Args:
            sampleFrames (list): a collections of frames from the camera

        Returns:
            int: the number of track locations found (even if it hasn't found them all)
        """
        for frame in sampleFrames:
            locationsFound = {}
            
            greenMask = cv.inRange(frame, *self.__GREEN_RANGE)
            # detector works better finding black dots on white background, so I invert the mask
            greenMask = cv.bitwise_not(cv.blur(greenMask, (15,15)))
            orangeMask = cv.inRange(frame, *self.__ORANGE_RANGE)
            orangeMask = cv.bitwise_not(cv.blur(orangeMask, (15,15)))
            
            for loc in self.__detector.detect(greenMask):
                # each 'loc' has a '.pt' attribute which I can index into to get their x and y
                locationsFound[(int(loc.pt[0]), int(loc.pt[1]))] = TRACK_STRAIGHT
                
            for loc in self.__detector.detect(orangeMask):
                locationsFound[(int(loc.pt[0]), int(loc.pt[1]))] = TRACK_TURN
                
            # save and break out the loop if we've found them all    
            if len(locationsFound) == NUM_TRACK_LOCATIONS:
                self.__trackLocations = locationsFound
                break
        
        # in case 0 frames are passed in and this raises an error for undefined locationsFound
        if len(sampleFrames) > 0: 
            return len(locationsFound)
        else:
            return 0
        
    def checkCameraConnected(self) -> bool:
        """Checks if the camera is actually sending the live video feed to me. 
        If the camera is not connected, a screen with 3 blue loading dots is shown instead. 
        This method checks if those blue dots are present. If yes, then the camera is not connected
        and the method should return False.
        
        Returns:
            bool: True if blue dots can't be found, meaning the camera feed is connected.
        """
        resultForEachFrame = []
        # take 3 repeat readings
        for _ in range(3):
            success, frame = self.__cameraFeed.read()
            if not success:
                resultForEachFrame.append(False)
                
            blueMask = cv.inRange(frame, *self.__BLUE_RANGE)
            blueMask = cv.bitwise_not(cv.blur(blueMask, (5,5)))
            blueBlobsXCoords = sorted([int(dot.pt[0]) for dot in self.__detector.detect(blueMask)])
            # check dots x coords to be certain it's the loading dots, not other random blue dots
            if blueBlobsXCoords == LOADING_DOTS_X_COORDS:
                resultForEachFrame.append(False)
            else:
                resultForEachFrame.append(True)
        
        return sum(resultForEachFrame) > 1
    
    def countCarPixelsAndTrackLocations(self) -> tuple:
        """gathers sample frames first, then uses these to train the background subtractor,  
        find the mean number of moving pixels and the number of track locations.

        Returns:
            tuple: the mean number of moving pixels found and the number of track locations found
        """
        sampleFrames = self.__gatherSampleFrames()
        if sampleFrames is INVALID:
            return 0, 0
        
        self.__trainBackground(sampleFrames)
        averageNumCarPixels = self.__getAverageNumCarPixels(sampleFrames)
        
        # use the same frames to find track locations so I dont waste time getting more frames
        numTrackLocations = self.__findAndSaveTrackLocations(sampleFrames)
        
        return averageNumCarPixels, numTrackLocations
        

# ==================== Training ========================================
    @staticmethod
    def __calcAverageLocation(mask: np.array) -> tuple:
        """calculate the mean x and y position of all the positive pixels in the mask given. 
        returns invalid if the mask is empty.

        Args:
            mask (np.array): the mask of the camera image

        Returns:
            tuple: meanX, meanY 
        """
        xCoords, yCoords = np.where(mask == 255)
        
        if len(xCoords) > 0:
            return int(np.mean(xCoords)), int(np.mean(yCoords))
        else:
            return INVALID

    def __getCarLocationAndTimeOfMeasurement(self) -> tuple:
        """uses the camera to find the cars location and saves the time when the frame was taken.

        Returns:
            tuple: the car's position and the time the frame was taken.
        """
        success, frame = self.__cameraFeed.read()
        timeOfMeasurement = time()
        if not success:
            return INVALID
        
        foreGroundMask = self.__backgroundSubtractor.apply(frame)
        foreGroundMask = cv.blur(foreGroundMask, (5,5))
        
        carLocation = self.__calcAverageLocation(foreGroundMask)
        if carLocation is INVALID:
            return INVALID
        return carLocation, timeOfMeasurement
        
    def __pixelsToMillimeters(self, distancePixels: float) -> float:
        """uses the constant I defined to convert from pixels to millimeters

        Args:
            distancePixels (float): the distance in pixels between two points on the camera image

        Returns:
            float: the distance in millimeters of the real world
        """
        return distancePixels * MILLIMETERS_PER_PIXEL
    
    def __calcDistancePixels(self, startCoords: tuple, endCoords: tuple) -> float:
        """uses the 'distance between two points' formula to calculate the distance in pixels

        Args:
            startCoords (tuple): the x, y pixel location of one point
            endCoords (tuple): the x, y pixel locations of the other point

        Returns:
            float: the distance between the two points in pixels
        """
        return sqrt(((endCoords[0] - startCoords[0]) ** 2) + ((endCoords[1] - startCoords[1]) ** 2))
            
    def __getCarSpeed(self, startCoords: tuple, endCoords: tuple, timeSeconds: float) -> float:
        """calculates the car's speed in the real world in millimeters per second

        Args:
            startCoords (tuple): the pixel x, y of one point
            endCoords (tuple): the pixel x, y of the other points
            timeSeconds (float): the time taken to travel between those two points

        Returns:
            float: the speed of the car in millimeters per second
        """
        distanceMillimeters = self.__pixelsToMillimeters(self.__calcDistancePixels(startCoords,
                                                                                   endCoords))
        return distanceMillimeters / timeSeconds
        
    def __getNextTrackLocationInfo(self, carStartCoords: tuple, carEndCoords: tuple) -> tuple:
        # save the initial distance of the car from each track location
        distancePixelsFromEachLocation = {}
        for location in self.__trackLocations:
            # units are irrelevent here as they all have the same ones. I'm using pixels as its 
            # more efficient than converting to millimeters every time.
            distancePixels = self.__calcDistancePixels(carStartCoords, location)
            distancePixelsFromEachLocation[location] = distancePixels
            
        # get the initial 2 closest track locations
        # self.__trackLocations is guaranteed to be populated with NUM_TRACK_LOCATIONS locations
        # (validation routine) and NUM_TRACK_LOCATIONS >= 2, (checked for in the constructor)
        # hence exception handling is not required, as nsmallest(2,...) will always return 2 values
        location1, location2 = nsmallest(2, distancePixelsFromEachLocation,
                                        key=distancePixelsFromEachLocation.get)
        
        
        # check which location has their distance decreasing (this will be the next location)
        newLocation1Distance = self.__calcDistancePixels(carEndCoords, location1)
        newLocation2Distance = self.__calcDistancePixels(carEndCoords, location2)
        deltaDistance1 = newLocation1Distance - distancePixelsFromEachLocation[location1]
        deltaDistance2 = newLocation2Distance - distancePixelsFromEachLocation[location2]
        if deltaDistance1 < deltaDistance2:
            # the final distance to corner should be converted to millimeters
            return location1, self.__pixelsToMillimeters(newLocation1Distance) 
        else:
            return location2, self.__pixelsToMillimeters(newLocation2Distance) 
              
    def getCarInfo(self) -> dict:
        """calls all the necessary functions to get all the needed information. It stores all
        of this in a dictionary so that it can easily be returned.

        Returns:
            dict: all the information collected into this dictionary.
        """
        info = {}
        # getCarLocationAndTimeOfMeasurement doesn't always return 2 values so I cant use:
        # startCoords, startTime = getCarLocationsAndTimeOfMeasurement() as it will cause an error.
        returnInfo = self.__getCarLocationAndTimeOfMeasurement()
        if returnInfo is INVALID:
            return INVALID
        else:
            startCoords, startTime = returnInfo
        
        returnInfo = self.__getCarLocationAndTimeOfMeasurement()
        if returnInfo is INVALID:
            return INVALID
        else:
            endCoords, endTime = returnInfo
        
        trackLocationInfo = self.__getNextTrackLocationInfo(startCoords, endCoords)
        if trackLocationInfo is INVALID:
            return INVALID
        else:
            nextTrackLocationCoords, nextTrackLocationDistMillimeters = trackLocationInfo
        
        # store data neatly to be returned
        info["location"] = endCoords
        info["speed"] = self.__getCarSpeed(startCoords, endCoords, (endTime - startTime))
        info["timeOfMeasurement"] = endTime
        info["nextTrackLocation"] = nextTrackLocationCoords
        info["nextTrackLocationDistanceMillimeters"] = nextTrackLocationDistMillimeters
        info["nextTrackLocationType"] = self.__trackLocations[nextTrackLocationCoords]
        return info
          
        
if __name__ == '__main__':
    c = CameraInput()