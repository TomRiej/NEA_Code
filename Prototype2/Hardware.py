from Constants import *

from serial import Serial
from time import time
from threading import Thread


class HardwareController:
    def __init__(self) -> None:
        """intitialises communitcation with the serial port and necessary attributes
        """
        self.__serialPort = Serial(SERIAL_PORT_NAME,
                                   SERIAL_BAUD_RATE,
                                   timeout=SERIAL_READ_TIMEOUT)
        
        # attributes for hardware output
        self.__previousServoAngle = -1
        
        # attributes for hardware input
        self.__ENCODING = "utf-8"
        
        self.__speed = 0.0
        self.resetSensorActivations()
        
        self.__measureLapTimes = False
        self.__mostRecentLapTime = EMPTY
        
        self.__continueReading = False
        
    # ==================== General ========================================
    def closeSerial(self):
        """stop the car and then close the serial port correctly.
        """
        self.stopCar()
        self.__serialPort.close()
    
    # ==================== Hardware output ======================================== 
    def angleIsValid(self, angle: int) -> bool:
        """validating the angle to be within the angle range specified in constants

        Args:
            angle (int): the angle

        Returns:
            bool: True if in range, False otherwise
        """
        # 'range[0] <= test <= range[1]' is faster than 'test in range(*range)'
        return SERVO_RANGE[0] <= angle <= SERVO_RANGE[1]
    
    def setServoAngle(self, angle: int) -> None:
        """validates the angle, makes sure the servo isn't already at that angle,
        then converts it to binary, then sends it on the serial port.

        Args:
            angle (int): the desired angle
        """
        if self.angleIsValid(angle):
            if angle != self.__previousServoAngle:
                self.__serialPort.write(angle.to_bytes(1, byteorder="little"))
                self.__previousServoAngle = angle
        elif DEBUG:
            print("Angle was not in servo range")
            
    def stopCar(self) -> None:
        """sets the servo angle to the minimum possibe angle in the servo range.
        """
        self.setServoAngle(SERVO_RANGE[0])
    
    # ==================== Hardware input ======================================== 
    def __calcSpeed(self, timeMillis: float) -> float:
        """calculates the speed of the car in millimeters per second

        Args:
            timeMillis (float): the time between sensor activations

        Returns:
            float: the speed of the car
        """
        return DISTANCE_BETWEEN_MAGNETS / (timeMillis/1000) if timeMillis != 0 else 0.0
    
    def __readSerialPort(self) -> None:
        """target method for a thread responible for reading the input from the hall sensors.
        It is responisble for reading the data from the serial port, then converting that from 
        bytes to a string. From this, I can get new information on the car's speed and laptimes.
        """
        while self.__continueReading:
            # get the data on the serial port
            lineAsBytes = self.__serialPort.readline()
            lineAsString = lineAsBytes.decode(self.__ENCODING)
            
            if lineAsString != EMPTY:
                # the arduino script returns the information in a format which allows for this
                sensorNumber, timeMillis = lineAsString.split(" ")
                self.__mostRecentSensorActivated = sensorNumber
                self.__speed = self.__calcSpeed(float(timeMillis))
                
                # check if the car has passed the finish line and if we should measure lap times
                if self.__measureLapTimes and sensorNumber == START_FINISH_SENSOR_NUMBER:
                    # only measure a laptime if all the sensors have been activated at least once
                    # after a reset: ensure timestamps in __sensorActivaions are since the reset.
                    if self.getNumSensorsActivated() == NUM_HALL_SENSORS:
                        self.__mostRecentLapTime = time() - self.__sensorActivations[sensorNumber]
                
                self.__sensorActivations[sensorNumber] = time()
                
    def getCarInfo(self) -> dict:
        """returns the car's speed and time of measurement in a dictionary 

        Returns:
            dict: the information on the car
        """
        if self.__mostRecentSensorActivated != EMPTY:
            return {
                "speed": self.__speed,
                "timeOfMeasurement": self.__sensorActivations[self.__mostRecentSensorActivated]
            }
        return EMPTY
    
    def getNewLapTime(self) -> float: #CHECK float return
        """if there is a new laptime, it is returned. Otherwise empty is returned

        Returns:
            float: the new lap time.
        """
        if self.__mostRecentLapTime is not EMPTY:
            newLapTime = self.__mostRecentLapTime
            self.__mostRecentLapTime = EMPTY
            return newLapTime
        else:
            return EMPTY
    
    def getNumSensorsActivated(self) -> int:
        """method to get the number of sensors activated for the validation frame.

        Returns:
            int: the number of sensors activated
        """
        return len(self.__sensorActivations) 
        
    def resetSensorActivations(self) -> None:
        """resets the sensor activations dictionary and most recent sensor activated
        """
        self.__sensorActivations = {}
        self.__mostRecentSensorActivated = EMPTY
                 
    def startMeasuringLapTimes(self) -> None:
        """method to start measuring lap times. 
        stop measuring lap times isn't needed.
        """
        self.__measureLapTimes = True
        if DEBUG:
            print("started measuring laptimes")             
                        
    def startReadingSerial(self) -> None:
        """method to start a thread for reading.
        """
        # check if there is already a reading thread active
        if not self.__continueReading:
            # creating a thread for reading in, so I dont disturb the UI that uses this module
            self.__thread = Thread(target=self.__readSerialPort)
            self.__continueReading = True
            # clear the input buffer so I only read the newest information. 
            self.__serialPort.reset_input_buffer()
            self.__thread.start()
        elif DEBUG:
            print("reading has already started")
            
    def stopReadingSerial(self) -> None:
        """method to stop the thread for reading
        """
        self.__continueReading = False
        self.__thread.join()
        
    
        
            
                
                
        