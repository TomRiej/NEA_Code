import cv2
import numpy as np

cap = cv2.VideoCapture(0)
fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
fgbg2 = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
fgbg3 = cv2.createBackgroundSubtractorMOG2(detectShadows=False)

while True:
    _, frame = cap.read()
    if frame is None:
        print("no frame")
        break
