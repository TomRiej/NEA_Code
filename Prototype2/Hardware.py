from Constants import *

from serial import Serial
from time import time
from threading import Thread


class HardwareController:
    def __init__(self) -> None:
        self.__serialPort = Serial(SERIAL_PORT_NAME,
                                   SERIAL_BAUD_RATE,
                                   timeout=SERIAL_READ_TIMEOUT)
        
        # hardware output: servo controll
        self.__previousServoAngle = -1
        
        # hardware input
        self.__ENCODING = "utf-8"
        
        self.__speed = 0.0
        self.resetSensorActivations()
        
        self.__measureLapTimes = False
        self.__mostRecentLapTime = EMPTY
        
        self.__continueReading = False
        
    # ==================== General ========================================
    def closeSerial(self):
        self.stopCar()
        self.__serialPort.close()
    
    # ==================== Hardware output ======================================== 
    def angleIsValid(self, angle: int) -> bool:
        return SERVO_RANGE[0] <= angle <= SERVO_RANGE[1]
    
    def setServoAngle(self, angle: int) -> None:
        if self.angleIsValid(angle):
            if angle != self.__previousServoAngle:
                self.__serialPort.write(angle.to_bytes(1, byteorder="little"))
                self.__previousServoAngle = angle
        elif DEBUG:
            print("Angle was not in servo range")
            
    def stopCar(self) -> None:
        self.setServoAngle(SERVO_RANGE[0])
    
    # ==================== Hardware input ======================================== 
    def getCarInfo(self) -> dict: # REFINE
        if self.__mostRecentSensorActivated != EMPTY:
            info = {}
            # info["sensorActivated"]  
            info["speed"] = self.__speed
            info["timeOfMeasurement"] = self.__sensorActivations[self.__mostRecentSensorActivated]
            return info
        return EMPTY
    
    def __calcSpeed(self, timeMillis: float) -> float:
        return DISTANCE_BETWEEN_MAGNETS / (timeMillis/1000) if timeMillis != 0 else 0.0
    
    def getNewLapTime(self) -> int: # REFINE
        if self.__mostRecentLapTime != EMPTY:
            tempLapTime = self.__mostRecentLapTime
            self.__mostRecentLapTime = EMPTY
            return tempLapTime
        else:
            return EMPTY
        
    def resetSensorActivations(self) -> None:
        self.__sensorActivations = {}
        self.__mostRecentSensorActivated = EMPTY
        
    def getNumSensorsActivated(self) -> int:
        return len(self.__sensorActivations)    
    
    # Read Thread Target
    def __readSerialPort(self) -> None: # REFINE
        while self.__continueReading:
            # get the data on the serial port
            lineAsBytes = self.__serialPort.readline()
            lineAsString = lineAsBytes.decode(self.__ENCODING)
            if lineAsString != EMPTY:
                sensorNumber, timeMillis = lineAsString.split(" ")
                self.__mostRecentSensorActivated = sensorNumber
                self.__speed = self.__calcSpeed(float(timeMillis))
                if self.__measureLapTimes and sensorNumber == START_FINISH_SENSOR_NUMBER:
                    if len(self.__sensorActivations) == NUM_HALL_SENSORS:
                        self.__mostRecentLapTime = time() - self.__sensorActivations[sensorNumber]
                self.__sensorActivations[sensorNumber] = time()
                
    def startReadingSerial(self) -> None:
        # check if there is already a reading thread active
        if not self.__continueReading:
            # creating a thread for reading in, so I dont disturb the UI that uses this module
            self.__thread = Thread(target=self.__readSerialPort)
            self.__continueReading = True
            self.__serialPort.reset_input_buffer()
            self.__thread.start()
        elif DEBUG:
            print("reading has already started")
            
    def stopReadingSerial(self) -> None:
        self.__continueReading = False
        self.__thread.join()
        
    def startMeasuringLapTimes(self) -> None:
        self.__measureLapTimes = True
        if DEBUG:
            print("started measuring laptimes")
        
            
                
                
        