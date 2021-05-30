import cv2 as cv
import numpy as np

greenLower = np.array([63, 185, 170])
greenUpper = np.array([83, 225, 210])
orangeLower = np.array([35, 140, 230])
orangeUpper = np.array([55, 180, 255])

cam = cv.VideoCapture(1)
detector = cv.SimpleBlobDetector_create()

while True:
    _, frame = cam.read()
    greenMask = cv.inRange(frame, greenLower, greenUpper)
    greenMask = cv.bitwise_not(cv.blur(greenMask, (15,15)))
    orangeMask = cv.inRange(frame, orangeLower, orangeUpper)
    orangeMask = cv.bitwise_not(cv.blur(orangeMask, (15,15)))
    
    greenKeyPoints = detector.detect(greenMask)
    orangeKeyPoints = detector.detect(orangeMask)

    for object in greenKeyPoints:
        x = int(object.pt[0])
        y = int(object.pt[1])
        cv.circle(frame, (x,y), 50, (0,255,0), 3)
        
    for object in orangeKeyPoints:
        x = int(object.pt[0])
        y = int(object.pt[1])
        cv.circle(frame, (x,y), 50, (0,0,255), 3)

        
    cv.imshow("frame", frame)
    # cv.imshow("g", greenMask)
    # cv.imshow("o", orangeMask)
    
    key = cv.waitKey(1)
    if key == 27:
        break