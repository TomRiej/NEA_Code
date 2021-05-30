import serial
from time import sleep

ser = serial.Serial("/dev/tty.usbmodem14101", 9600, timeout=1)
sleep(2)

ENCODING = "utf-8"

for i in range(50):
    line = ser.readline()
    strline = line.decode(ENCODING)
    if strline != "":
        print(strline.strip())
    
    
    
ser.close()