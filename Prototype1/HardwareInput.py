  # Requirements
# getInputSuccess()
#
import serial
from time import sleep, time
from threading import Thread


class HallInput:
    def __init__(self, distBetweenMagnets: float) -> None:
        self.__ser = serial.Serial("/dev/tty.usbmodem14101", 9600, timeout=.5)
        sleep(2) # allow time for the serial object to connect to port
        
        self.__DIST_BETWEEN_MAGNETS = distBetweenMagnets
        self.__ENCODING = "utf-8"
        self.__EMPTY = ""
     
        self.__speed = 0.0 
        self.__displacement = 0
        
        self.__sensorsPassed = {}
        self.__continueReading = False


    def __calcSpeed(self, timeMillis: int) -> float:
        if timeMillis == 0:
            print("Time value is 0 causing division by 0 error")
            return 0.0
        else:
            timeSec = timeMillis / 1000
            return self.__DIST_BETWEEN_MAGNETS / timeSec
        
    def __readSerialPort(self) -> None:
        while self.__continueReading:
            line = self.__ser.readline()
            strLine = line.decode(self.__ENCODING)
            if strLine != self.__EMPTY:
                disp, timeTaken = strLine.split(" ")
                self.__displacement = int(disp)
                self.__speed = self.__calcSpeed(float(timeTaken))
                self.__sensorsPassed[self.__displacement] = time()
            
    def startReading(self):
        # only start reading if it isn't already started
        if not self.__continueReading:
            # creating a thread for reading in, so i dont disturb any loops that use this module
            self.__thread = Thread(target=self.__readSerialPort)
            self.__continueReading = True
            self.__thread.start()
        else:
            print("reading has already started")
        
    def stopReading(self):
        self.__continueReading = False
        self.__thread.join()
        
    def clearSensorsPassed(self):
        self.__sensorsPassed = {}
            
    def getSensorsPassed(self):
        return self.__sensorsPassed
            
    def getSpeed(self) -> float:
        return self.__speed
    
    def getDisplacement(self) -> int:
        return self.__displacement
    
    def closeSerial(self) -> None:
        self.__ser.close()
        
        
if __name__ == '__main__':
      
    # 10cm = 0.1 m           
    hallReader = HallInput(0.1)

    for i in range(20):
        hallReader.readSerialPort()
        print(f"SensorNumber: {hallReader.getDisplacement()} Speed: {hallReader.getSpeed()}")
    print(hallReader.getSensorsPassed())
        