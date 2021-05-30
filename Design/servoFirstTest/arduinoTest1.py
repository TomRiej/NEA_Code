import serial
from time import sleep

ser = serial.Serial("/dev/tty.usbmodem14101", 9600, timeout=1)
sleep(2)

param1 = 20 # for some reason, 0 here makes it over rotate and 20 looks good
param2 = 90
param3 = 180

for i in range(5): # loop()
    ser.write(param1.to_bytes(1, byteorder="little"))
    sleep(1)
    ser.write(param2.to_bytes(1, byteorder="little"))
    sleep(1)
    ser.write(param3.to_bytes(1, byteorder="little"))
    sleep(1)
    ser.write(param2.to_bytes(1, byteorder="little"))
    sleep(1)
    
ser.close()

