import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
 
WINDOW_SIZE = (650,500)
BG_COLOUR = "#FFFFFF"
RED = "#FF0000"
GREEN = "#20CC20"
FONT = "Verdana"
PATH = "/Users/Tom/Desktop/Education/CS-A-level/NEA/Media/"
REFRESH_AFTER = 1000 # 1000ms = 1 second


class MyFrame(tk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        tk.Frame.__init__(self, master,
                          width=WINDOW_SIZE[0],
                          height=WINDOW_SIZE[1],
                          bg=BG_COLOUR)
        
        self._title = tk.Label(self,
                                font=(FONT, 35),
                                text="title text")
        
        self._infoMessage = tk.Label(self,
                                      font=(FONT,15),
                                      text= "info text")
        
    def showContent(self): # to be overridden later
        pass
    
    def delete(self) -> None:
        self.grid_forget()
        self.destroy()
        

class StartFrame(MyFrame):
    def __init__(self, master: tk.Tk, changeFrameFunc) -> None:
        super().__init__(master)
        self.__IMAGESIZE = (200,75)
        
        # https://stackoverflow.com/questions/54716337/tkinter-how-to-place-image-into-a-frame
        # Used this solution by Partho63 to add an image to the frame.
        # Best practice is to use a canvas.
        self.__canvasForImage = tk.Canvas(self,
                                   width=WINDOW_SIZE[0],
                                   height=100)
        
        image = Image.open(PATH+"FormulAI_Logo.png")
        self.__canvasForImage.image = ImageTk.PhotoImage(image.resize(self.__IMAGESIZE, Image.ANTIALIAS))
        self.__canvasForImage.create_image(WINDOW_SIZE[0]//2, 50,
                                    image=self.__canvasForImage.image)
        
        self._title.config(text="Welcome To FormulAI!")
        
        
        self._infoMessage.config(text=
        """\nFormulAI is an A-level NEA project designed by Tom Rietjens at Dubai College. \n \n
        Please press the start button below to proceed!\n\n""")  
        
        self.__startButton = tk.Button(self,
                                height=2,
                                width=10,
                                text="Start!",
                                font=(FONT, 25),
                                command=changeFrameFunc)
        
    def showContent(self) -> None:
        self.__canvasForImage.grid(row=0)
        self._title.grid(row=1)
        self._infoMessage.grid(row=2)
        self.__startButton.grid(row=3) 


class StatusLabel:
    def __init__(self, master: tk.Tk, infoText: str) -> None:
        self.__infoText = tk.Label(master,
                                   text=infoText +": ",
                                   font=(FONT, 25))
        self.__statusText = tk.Label(master,
                                     text="Failed",
                                     fg=RED,
                                     font=(FONT, 25))
    
    def grid(self, row: int) -> None:
        self.__infoText.grid(row=row, column=0)
        self.__statusText.grid(row=row, column=1)
        
    def setStatus(self, status: bool) -> None:
        self.__status = status
        if self.__status:
            self.__statusText.config(text="Passed",
                                     fg=GREEN)
        else:
            self.__statusText.config(text="Failed",
                                     fg=RED)


class ValidationFrame(MyFrame):
    def __init__(self, master: tk.Tk, changeFrameFunc, retryFunc) -> None:
        super().__init__(master)
        self._title.config(text="Validation Screen")
        
        self._infoMessage.config(text=
    """This is the screen where you must make sure all the inputs
    are working as expected.\n""")
        
        self.__statuses = [StatusLabel(self, "Input from iPhone camera"),
                           StatusLabel(self, "Car is seen by the camera"),
                           StatusLabel(self, "Track is seen by the camera"),
                           StatusLabel(self, "Input from on-track sensors")]
        
        self.__feedbackLabel = tk.Label(self, font=(FONT, 15))
        self.__allValid = False
        
        self.__retryButton = tk.Button(self, 
                                       height=2,
                                       width=10,
                                       text="Retry",
                                       font=(FONT, 25),
                                       command=retryFunc)
        
        self.__startTrainingButton = tk.Button(self,
                                               height=2,
                                               width=15,
                                               text="Start Training!",
                                               font=(FONT, 25),
                                               command=changeFrameFunc)

        
    def setStatuses(self, allStatuses: list) -> None:
        self.__allValid = True
        self.__feedbackLabel.config(text="All inputs are valid!\n",
                                    fg=GREEN)
        for i, statusLabel in enumerate(self.__statuses):
            if allStatuses[i]:
                statusLabel.setStatus(True)
            else:
                statusLabel.setStatus(False)
                self.__allValid = False
                self.__feedbackLabel.config(text="Please do the necessary fixes\n",
                                            fg=RED)
        
    def showContent(self) -> None:
        self._title.grid(row=0, columnspan=2)
        self._infoMessage.grid(row=1, columnspan=2)
        for i, statusLabel in enumerate(self.__statuses):
            statusLabel.grid(i+2)
        curRow = len(self.__statuses)+3
        self.__feedbackLabel.grid(row=curRow, columnspan=2)
        if self.__allValid:
            self.__startTrainingButton.grid(row=curRow+1, columnspan=2)
        else:
            self.__retryButton.grid(row=curRow+1, columnspan=2)
        
      
class TrainingFrame(MyFrame):
    def __init__(self, master: tk.Tk, changeFrameFunc, stopLoopFunc) -> None:
        super().__init__(master)
        # setting up Tkinter widgets
        self._title.config(text="Training Screen")
        
        self._infoMessage.config(text=
    """This is the screen which shows you the progress of the Reinforcement
    learning algorithm that is being applied to the car.""")
        
        self.__stopButton = tk.Button(self,
                                      height=2,
                                      width=15,
                                      text="STOP",
                                      fg=RED,
                                      font=(FONT, 25),
                                      command=stopLoopFunc)
        
        self.__endProgramButton = tk.Button(self,
                                               height=2,
                                               width=15,
                                               text="End Program",
                                               font=(FONT, 25),
                                               command=changeFrameFunc)
        # setting up the graphs
        # I'm using both:
        # https://www.geeksforgeeks.org/how-to-embed-matplotlib-charts-in-tkinter-gui/
        # https://pythonprogramming.net/embedding-live-matplotlib-graph-tkinter-gui/
        # to help me embed the graph into the window
        self.__fig = plt.Figure(figsize=(3,3), dpi=100)
        self.__fig.set_tight_layout(True)
        self.__myPlot = self.__fig.add_subplot(111)
        self.__canvasGraph = None
        
        
    def updateGraph(self, newData: list) -> None:
        xList = []
        yList = []
        for x, y in newData:
            xList.append(int(x))
            yList.append(int(y))
        self.__myPlot.clear()
        self.__myPlot.plot(xList, yList)
        self.__myPlot.set_xlabel("Lap Number")
        self.__myPlot.set_ylabel("Time Taken")
        self.__canvasGraph = FigureCanvasTkAgg(self.__fig, master=self)
        self.__canvasGraph.draw()        
        
    def showContent(self) -> None:
        self._title.grid(row=0, columnspan=2)
        self._infoMessage.grid(row=1, columnspan=2)
        if self.__canvasGraph is not None:
            self.__canvasGraph.get_tk_widget().grid(row=2, columnspan=2)
        self.__stopButton.grid(row=3, column=0, columnspan=1)
        self.__endProgramButton.grid(row=3, column=1, columnspan=1)
                

class MainApplication:
    def __init__(self, master: tk.Tk) -> None:
        self.__master = master
        self.__master.minsize(width=WINDOW_SIZE[0],
                              height=WINDOW_SIZE[1])
        self.__master.title("FormulAI")
        
        self.__startFrame = StartFrame(self.__master, self.__changeToNextFrame)
        self.__validationFrame = ValidationFrame(self.__master, self.__changeToNextFrame, self.__doValidationRoutine)
        self.__trainingFrame = TrainingFrame(self.__master, self.__changeToNextFrame, self.__stopTraining)
        
        self.__currentFrame = self.__startFrame
        
    def __changeToNextFrame(self) -> None:
        if self.__currentFrame == self.__startFrame:
            self.__currentFrame.delete()
            self.__currentFrame = self.__validationFrame
            self.__doValidationRoutine(True)
        elif self.__currentFrame == self.__validationFrame:
            self.__currentFrame.delete()
            self.__currentFrame = self.__trainingFrame
            self.__continueTraining = True
            self.__doTrainingLoop()
        elif self.__currentFrame == self.__trainingFrame:
            self.__trainingFrame.delete()
            self.__master.destroy()
            self.__endProgram()
            
    def showCurrentFrame(self) -> None:
        self.__currentFrame.pack()
        self.__currentFrame.showContent()
        
    def __doValidationRoutine(self, toFail:bool=False) -> None:
        if toFail:
            output = [True, True, False, True]
        else:
            output = [True for x in range(4)]
        self.__validationFrame.setStatuses(output)
        self.showCurrentFrame()
        
    def __doTrainingLoop(self) -> None:
        self.showCurrentFrame()
        # do the training
        print("trained")
        # to test the graph updating:
        newData = []
        with open(PATH+"sampleData.txt", "r") as file:
            for line in file:
                line = line.strip()
                x,y = line.split(",")
                newData.append((x,y))
        self.__currentFrame.updateGraph(newData)
        
        if self.__continueTraining:
            self.__master.after(REFRESH_AFTER, self.__doTrainingLoop)
        else:
            print("training stopped")
    
    def __stopTraining(self) -> None:
        self.__continueTraining = False
    
    def __endProgram(self) -> None:
        print("Stopping Training loop...")
        self.__stopTraining()
        print("Closing Serial Ports...")
        print("Closing Camera Input...")
        # close everything
        print("\nComplete")
        
        

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    app.showCurrentFrame()
    root.mainloop()