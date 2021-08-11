import serial
from time import sleep


class ServoController:
    def __init__(self, mini: int, maxi: int) -> None:
        self.__ser = serial.Serial("/dev/tty.usbmodem14101", 9600)
        sleep(2)
        self.__prevAngle = -1
        self.__VALID_RANGE = [mini, maxi+1]
        
    
    def angleIsValid(self, angle: int) -> bool:
        if angle in range(*self.__VALID_RANGE): # *[] expands the list
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
            
    def closeSerial(self) -> None:
        self.__ser.close()
            

# ranges = [[0,180], [20,160], [40,140], [0,0]]  
# for ran in ranges:
#     controller = ServoController(*ran)
#     print(f"Range: {ran[0]} -> {ran[1]}")
#     for i in range(0, 201, 10):
#         print(f"attempting set angle to {i}")
#         controller.setAngle(i)
#         sleep(1)
#     controller.closeSerial()
#     print()
if __name__ == '__main__':
    con = ServoController(40,90)
    for i in range(10):
        con.setAngle(50)
        sleep(1)
        con.setAngle(60)
        sleep(1)
        con.setAngle(70)
        sleep(1)
        con.setAngle(80)
        sleep(1)
        con.setAngle(90)
        sleep(1)
    con.closeSerial()
    

        
        
        
        
        