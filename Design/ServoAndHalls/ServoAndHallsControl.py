import sys
sys.path.append("/Users/Tom/github/NEA_Code/Design/servoFirstTest")
sys.path.append("/Users/Tom/github/NEA_Code/Design/multiple_halls")

from HallInput import *
from ServoController import *
from time import sleep
import threading

class readerThread:
    def __init__(self, reader):
        self.__hallReader = reader
        self.__thread = threading.Thread(target=self.constantRead)
        self.__continue = True
        
        
    def constantRead(self):
        while self.__continue:
            self.__hallReader.readSerialPort()
            print(f"SensorNumber: {self.__hallReader.getDisplacement()} Speed: {self.__hallReader.getSpeed()}")

    def start(self):
        self.__thread.start()
            
    def stop(self):
        self.__continue = False
        self.__thread.join()
        print("finish")
            
# def constantRead():
#     for i in range(20):
#         hallReader.readSerialPort()
#         print(f"SensorNumber: {hallReader.getDisplacement()} Speed: {hallReader.getSpeed()}")

if __name__ == '__main__':
    hallReader = HallInput(88)
    con = ServoController(0,90)
    
    readThread = readerThread(hallReader)
    readThread.start()
    con.setAngle(40)
    sleep(3)
    con.setAngle(75)
    sleep(0.3)
    con.setAngle(62)
    sleep(20)
    # for i in range(10):
    #     con.setAngle(50)
    #     sleep(1)
    #     con.setAngle(60)
    #     sleep(0.5)
    #     con.setAngle(70)
    #     sleep(0.5)
    #     con.setAngle(80)
    #     sleep(0.5)
    #     # con.setAngle(90)
    #     # sleep(0.5)
        
    con.setAngle(30)
    readThread.stop()
    hallReader.closeSerial()
    con.closeSerial()
    
