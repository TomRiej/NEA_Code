import cv2 as cv
import numpy as np


class Calibrator:
    def __init__(self):
        self.__y, self.__x = 500,500
        self.__cam  = cv.VideoCapture(1)
        
    def __onClick(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            self.__x = x
            self.__y = y

    def run(self):
        while True:
            _, frame = self.__cam.read()
            cv.setMouseCallback("frame", self.__onClick)
            
            frame[self.__y, self.__x] = (0,255,0)
            cv.circle(frame, (self.__x, self.__y), 20, (0,255,0), 3)
            
            cv.imshow("frame", frame)
            key = cv.waitKey(1)
            if key == 32:
                _, newFrame = self.__cam.read()
                print(newFrame[self.__y,self.__x])
            if key == 27:
                break
            
cal = Calibrator()
cal.run()

# green
# [ 81 205 190]
# [ 83 205 188]
# [ 86 202 190]
# orange
# [ 45 117 194]
# [ 45 117 194]
# [ 48 117 197]
# [ 42 116 193]
# [ 47 116 194]
# [ 64 149 240]
# [ 62 148 230]
# [ 57 132 225]
# [ 54 134 215]
# [ 55 134 223]
# [ 58 136 221]
# [ 59 135 216]