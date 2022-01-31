from random import random
from Constants import *


class SimulateTrack:
    def __init__(self, timeStep: float) -> None:
        self.__lapsCompleted = 0
        self.resetCar()
        self.__distanceToCorner = 99            # cm
        
        self.__corners = ["0", "1", "1", "0", "1", "1"]
        self.__currentCorner = 0
        
        self.__timeStep = timeStep              # seconds
        
        
    def getStateAndSpeed(self) -> tuple:
        state = ""
        state += self.__corners[self.__currentCorner]
        state += "{:02d}".format(int(self.__distanceToCorner))
        if self.__deslotted:
            state += "000"
        else:
            state += "{:03d}".format(int(self.__speed))
        return state, (self.__speed if not self.__deslotted else 0)
    
    def getDeslotted(self) -> bool:
        return self.__deslotted
    
    def getLapsCompleted(self) -> int:
        return self.__lapsCompleted
    
    def resetCar(self) -> int:
        self.__deslotted = False
        self.__prevSpeed = 0                    # cm / s
        self.__speed = 0                        # mm / s
        
    @ staticmethod
    def __normalise(value: int, low: int = SERVO_RANGE[0], high: int = SERVO_RANGE[1]) -> float:
        return ((value-low)/(high-low))
    
    @ staticmethod
    def __getSpeedFromAngle(angle: str) -> float:
        # linear relationship between angle and speed: highest angle -> highest speed (999)
        # add a bit of randomness as well
        return (SimulateTrack.__normalise(int(angle)) * 990) + ((random()*2 -1)*10)
    
    def __updateSpeed(self, action: str) -> None:
        self.__prevSpeed = self.__speed
        self.__speed = self.__getSpeedFromAngle(action)
    
    def __updateDistanceAndCorners(self) -> None:
        # calculating distance travelled in the given time: 
        # ie moving 200 mm /s in 0.5 seconds = 100mm
        self.__distanceToCorner -= (self.__speed/10) * self.__timeStep
        
        # if the distance to corner is -ve, we've passed the corner, 
        # so we need to update the next one
        if self.__distanceToCorner <= 0:
            # new max distance to corner
            self.__distanceToCorner = 99
            
            # check if completed a lap
            if self.__currentCorner == len(self.__corners)-1:
                self.__lapsCompleted += 1
                self.__currentCorner = 0
            else:
                self.__currentCorner += 1
    
    def __decideIfDeslotted(self) -> None:
        # Deciding if the car has deslotted
        # can can only deslot on turns, as it wont delsot on straight lines
        if self.__corners[self.__currentCorner] == "1":
            if self.__speed > 800:
                # with high momentum and speed, very high chance to delot
                if self.__prevSpeed > 800 and random() < 0.9:
                    self.__deslotted = True
                elif self.__prevSpeed < 400 and random() < 0.4:
                    self.__deslotted = True
                elif random() < 0.65:
                    self.__deslotted = True
                
            
            elif self.__speed > 650:
                if self.__prevSpeed > 800 and random() < 0.6:
                    self.__deslotted = True
                elif self.__prevSpeed < 400 and random() < 0.1:
                    self.__deslotted = True
                elif random() < 0.2:
                    self.__deslotted = True
                    
            elif self.__speed > 400:
                if self.__prevSpeed > 80 and random() < 0.2:
                    self.__deslotted = True
            
            # speeds below 400 are very likely to get stuck, which I call a deslot
            elif self.__prevSpeed > 800 and random() < 0.2:
                self.__deslotted = True
            elif self.__prevSpeed > 400 and random() < 0.5:
                self.__deslotted = True
            elif random() < 0.9:
                self.__deslotted = True
        
        if self.__deslotted:
            self.__lapsCompleted = 0
            
    
    def doAction(self, action: str) -> None:
        self.__updateSpeed(action)
        self.__updateDistanceAndCorners()
        self.__decideIfDeslotted()
        
                
        
        
        
                
            
                
