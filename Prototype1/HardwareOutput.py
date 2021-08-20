import serial

class ServoController:
    def __init__(self, portName, baudRate, angleRange) -> None:
        self.__ser = serial.Serial(portName, baudRate)
        
        self.__prevAngle = -1
        self.__VALID_RANGE = angleRange
        
    
    def angleIsValid(self, angle: int) -> bool:
        if self.__VALID_RANGE[0] <= angle <= self.__VALID_RANGE[1]: 
            return True                          
        else:
            return False
        
    def setAngle(self, angle: int) -> None:
        if self.angleIsValid(angle):
            if angle != self.__prevAngle:
                self.__ser.write(angle.to_bytes(1, byteorder="little"))
                self.__prevAngle = angle
        else:
            print("Angle was not within range specified by min and max")
            
    def stopCar(self):
        self.setAngle(self.__VALID_RANGE[0])
            
    def closeSerial(self) -> None:
        self.__ser.close()