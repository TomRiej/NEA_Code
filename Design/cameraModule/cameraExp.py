import cv2
import numpy as np

cap = cv2.VideoCapture(1)
fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
# blobDetector = cv2.SimpleBlobDetector_create()

# boundaries = [
#     ([17,74,26], [35,85,44]) #green
# ]

# bmax = 0
# bmin = 255
# gmax = 0
# gmin = 255
# rmax = 0
# rmin = 255

while True:
    _, frame = cap.read()
    if frame is None:
        print("no frame")
        break
    
    fgMask = fgbg.apply(frame)
    
    result = np.where(fgMask == 255)
    xCoords = result[1]
    yCoords = result[0]
    try:
        meanX = int(np.mean(xCoords))
        meanY = int(np.mean(yCoords))
    except ValueError:
        print("NaN error")
    
    cv2.circle(frame, (meanX, meanY), 50, (0,255,0), 3)
    
    key = cv2.waitKey(1)
    if key == 27:
        break
    
    cv2.imshow("Frame", frame)
    
    cv2.imshow("mask", fgMask)
    # cv2.imshow("Output", output)
    
# print(f"blue: max:{bmax} min:{bmin}")
# print(f"green: max:{gmax} min:{gmin}")
# print(f"red: max:{rmax} min:{rmin}")


# print("strer")
    # keypoints = blobDetector.detect(fgMask)
    # print("keypoints", keypoints)
    # output = cv2.drawKeypoints(frame, keypoints, np.array([]), (0,255,0))

    
    # meanVal = cv2.mean(frame, mask=fgMask)
    # print(meanVal)
    
    
    # print(fgMask)
    # output = cv2.bitwise_and(frame, frame, mask=fgMask)
    
    # cv2.rectangle(frame, (meanVal-50,meanVal-50), (meanVal+50,meanVal+50), (0,255,0), 3)
    # frame[0:200, 0:200] = (0, 255, 0)
    
    # for (lower,upper) in boundaries:
    #     lower = np.array(lower, dtype="uint8")
    #     upper = np.array(upper, dtype = "uint8")
        
    #     mask = cv2.inRange(frame, lower, upper)
    #     indecies = np.where()
    #     print(indecies)
        # coords = zip(indecies[0], indecies[1])
        # print(coords)
        # output = cv2.bitwise_and(frame, frame, mask=mask)
    
    # indies = np.where(frame[0] in range(42-5,42+5) and frame[1] in range(90-5,90+5) and frame[2] in range([40-5, 40+5]))
    # coords1 = zip(indies[0], indies[1])
    # for coord in coords1:
    #     frame[coord[0],coord[1]] = (0, 255, 0)
    
    
    # elif key == 32:
    #     tcoords = [[500,500]]
    #     for coord in tcoords:
    #         (b,g,r) = frame[coord[0], coord[1]]
            
    #         bmax = max(b, bmax)
    #         bmin = min(b, bmin)
    #         gmax = max(g,gmax)
    #         gmin = min(g, gmin)
    #         rmax = max(r, rmax)
    #         rmin = min(r, rmin)
        
            
    #         frame[coord[0],coord[1]] = (0,255,0)
    #         print(f"Pixel at {coord} - Red {r} Green {g} Blue {b}")
