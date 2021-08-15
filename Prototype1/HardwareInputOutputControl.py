  # Requirements
# 2 threads: one for input, one for output
# getInputSuccess()
# getRecentCarInfo()

from HardwareInput import *
from HardwareOutput import *
                
class HardwareController:
    def __init__(self, distanceBetweenMagnets):
        self.__hallEffectSensorInput = HallInput(distanceBetweenMagnets)
        self.__servoController = None
    
    def getNumHallInputs(self):
        return len(self.__hallEffectSensorInput.getSensorsPassed())
    
    def clearSensorsPassed(self):
        self.__hallEffectSensorInput.clearSensorsPassed()
    
    def startReading(self):
        self.__hallEffectSensorInput.startReading()
        
    def stopReading(self):
        self.__hallEffectSensorInput.stopReading()
        
    def close(self):
        self.__hallEffectSensorInput.closeSerial()
        
    
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