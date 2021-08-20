  # Requirements
# 2 threads: one for input, one for output
# getInputSuccess()
# getRecentCarInfo()

from HardwareInput import *
from HardwareOutput import *
                
class HardwareController:
    def __init__(self, portName, baudRate, timeout, distanceBetweenMagnets, angleRange):
        self.__hallEffectSensorInput = HallInput(portName, baudRate, timeout, distanceBetweenMagnets)
        self.__servoController = ServoController(portName, baudRate, angleRange)
    
    def getNumHallInputs(self):
        return len(self.__hallEffectSensorInput.getSensorsPassed())
    
    def clearSensorsPassed(self):
        self.__hallEffectSensorInput.clearSensorsPassed()
    
    def startReading(self):
        self.__hallEffectSensorInput.startReading()
        
    def stopReading(self):
        self.__hallEffectSensorInput.stopReading()
        
    def setServoAngle(self, angle):
        self.__servoController.setAngle(angle)
        
    def stopCar(self):
        self.__servoController.stopCar()
        
    def close(self):
        self.stopCar()
        self.__hallEffectSensorInput.closeSerial()
        self.__servoController.closeSerial()
        
    
if __name__=="__main__":
    from time import sleep
    h = HardwareController(0.1)
    for i in range(2):
        print("starting")
        h.startReading()
        for i in range(10):
            print(h.getNumHallInputs())
            sleep(1)
        h.stopReading()
        print("finished")
        sleep(2)