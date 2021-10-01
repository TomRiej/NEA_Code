import cv2 as cv

class CameraInput:
    def __init__(self):
        self.__cameraFeed = cv.VideoCapture(1)
        
        
    def getframe(self):
        _, frame = self.__cameraFeed.read()
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        return frame
        # while True:
        #     cv.imshow("f", frame)
        #     k = cv.waitKey(1)
        #     if k == 27:
        #         break
    
if __name__ == '__main__':  
    c = CameraInput()
    c.getframe()