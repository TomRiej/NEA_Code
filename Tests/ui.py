import tkinter as tk
from PIL import Image, ImageTk
from camera import CameraInput
import cv2 as cv


class App:
    def __init__(self, master):
        self.__master = master
        self.__master.title("main")
        self.__show = tk.Toplevel(self.__master)
        self.__show.title("show")
        self.__canvasForImage = tk.Canvas(self.__show,
                                          width=650,
                                          height=500)
        self.__canvasForImage.pack()
        self.__cam = CameraInput()
        
        
    def embedImage(self):
        image = self.__cam.getframe()
        self.__canvasForImage.delete("all")
        # while True:
        #     cv.imshow("f", image)
        #     k = cv.waitKey(1)
        #     if k == 27:
        #         break
        image = Image.fromarray(image)
        self.__canvasForImage.image = ImageTk.PhotoImage(image.resize((640, 360), Image.ANTIALIAS))
        self.__canvasForImage.create_image(650//2, 500//2,
                                           image=self.__canvasForImage.image)
        
        self.__master.after(1, self.embedImage)
        # self.__label = tk.Label(self.__master,
        #                         image=image)
        # self.__label.pack()
        
        
        
        
if __name__ == '__main__':
    root = tk.Tk()
    a = App(root)
    a.embedImage()
    root.mainloop()
    