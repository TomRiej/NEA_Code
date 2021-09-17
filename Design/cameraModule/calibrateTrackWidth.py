import cv2 as cv

cap = cv.VideoCapture(1)

def onClick(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        print("clicked at x: ", x)

print("the x coord of where you click is printed")
while True:
    _, frame = cap.read()
    
    cv.setMouseCallback("frame", onClick)
    cv.line(frame, (0, 50), (2000, 50), (0,255,0), 2)
    cv.imshow("frame",frame)
    
    key = cv.waitKey(1)
    if key == 27:
        break