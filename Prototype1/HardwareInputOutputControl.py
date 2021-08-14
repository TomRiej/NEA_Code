  # Requirements
# 2 threads: one for input, one for output
# getInputSuccess()
# getRecentCarInfo()
from threading import Thread


from HardwareInput import *
from HardwareOutput import *


# class needed so that I am able to stop the thread at will using
# class attributs with sufficient scope
# class readerThread:
#     def __init__(self, reader):
#         self.__hallReader = reader
#         self.__thread = Thread(target=self.constantRead)
#         self.__continue = True
        
        
#     def constantRead(self):
#         while self.__continue:
#             self.__hallReader.readSerialPort()
#             print(f"SensorNumber: {self.__hallReader.getDisplacement()} Speed: {self.__hallReader.getSpeed()}")

#     def start(self):
#         self.__thread.start()
            
#     def stop(self):
#         self.__continue = False
#         self.__thread.join()
#         print("finish")
        
        
        
class HardwareController:
    def __init__(self, distanceBetweenMagnets):
        self.__hallEffectSensorInput = HallInput(distanceBetweenMagnets)
        self.__servoController = None
    
    def getNumHallInputs(self):
        return len(self.__hallEffectSensorInput.getSensorsPassed())
    
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