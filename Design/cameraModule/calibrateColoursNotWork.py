import cv2 as cv
import numpy as np



class Calibrator:
    def __init__(self):
        self.__cam = cv.VideoCapture(0)
        self.__firstClick = True
        self.__rectCoords = []

    def __mouseClick(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            if self.__firstClick:
                self.__rectCoords.append((x,y))
                self.__firstClick = False
            else:
                self.__rectCoords.append((x,y))
                self.__firstClick = True
                
    def __drawRects(self, frame):
        numCoords = len(self.__rectCoords)
        if numCoords > 0:
            for i in range(0,numCoords,2):
                x,y = self.__rectCoords[i]
                if i < numCoords-1:
                    x2, y2 = self.__rectCoords[i+1]
                    cv.rectangle(frame, (x,y), (x2,y2), (255,255,255), 3)
                else:
                    break
            
    def __printAverageColour(self, frame):
        numCoords = len(self.__rectCoords)
        if numCoords > 0:
            for i in range(0,numCoords,2):
                x,y = self.__rectCoords[i]
                if i < numCoords-1:
                    x2, y2 = self.__rectCoords[i+1]
                    area = frame[y:y2, x:x2]
                    blues, greens, reds = [], [], []
                    for pixel in area:
                        blues.append(pixel[0])
                        greens.append(pixel[1])
                        reds.append(pixel[2])
                    print("blue", sum(blues)/len(blues))
                    print("green", sum(greens)/len(greens))
                    print("red", sum(reds)/len(reds))
                else:
                    break
            
            
    def run(self):
        while True:
            _, frame = self.__cam.read()
            if frame is None:
                break
            
            cv.setMouseCallback("frame", self.__mouseClick)
            self.__drawRects(frame)
            
            cv.imshow("frame", frame)
            key = cv.waitKey(1)
            if key == 27:
                self.__printAverageColour(frame)
                break
            
cal = Calibrator()
cal.run()
    
    