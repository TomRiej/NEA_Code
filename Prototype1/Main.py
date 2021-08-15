# Import built in modules for the UI
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from threading import Thread

from time import sleep, time
# Import all my modules:
from CameraModule import *
from HardwareInputOutputControl import *
# QLearning

# Defining constants 
  # UI
WINDOW_SIZE = (650,500)
BG_COLOUR = "#FFFFFF"
RED = "#FF0000"
GREEN = "#20CC20"  
BLUE = "#0e6cc9"
FONT = "Verdana"
PATH = "/Users/Tom/Desktop/Education/CS-A-level/NEA/Media/"
REFRESH_AFTER = 1000 # 1000ms = 1 second
LOGO_NAME = "FormulAI_Logo.png"
EMPTY = ""
  # Camera
GREEN_RANGE = [[70, 190, 160], [120, 255, 220]]
ORANGE_RANGE = [[50, 110, 200], [90, 190, 255]]
SAMPLE_ITERATIONS = 50
DESLOT_THRESHOLD = 0
NUM_TRACK_LOCATIONS = 6
  # Harware Input
DISTANCE_BETWEEN_MAGNETS = 50 # mm
NUM_HALL_SENSORS = 4
TIMEOUT = 10 # seconds
  # Hardware Output
# Servo angle range
# Stop angle
# Slow speed angle
  # Q Learning
# Parameters


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
        self.__master = master
        self.__IMAGESIZE = (200,75)
        
        # https://stackoverflow.com/questions/54716337/tkinter-how-to-place-image-into-a-frame
        # Used this solution by Partho63 to add an image to the frame.
        # Best practice is to use a canvas.
        self.__canvasForImage = tk.Canvas(self,
                                   width=WINDOW_SIZE[0],
                                   height=100)
        
        image = Image.open(PATH+LOGO_NAME)
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
        
        self.__errorHasOccured = False
        self.__quitButton = tk.Button(self,
                                      height=2,
                                      width=10,
                                      text="Quit",
                                      font=(FONT, 25),
                                      command=self.__master.destroy)
        
    def raiseError(self, errorMessage):
        self.__errorHasOccured = True
        self._infoMessage.config(text="\n"+errorMessage+"\n\n",
                                 fg=RED)
        self.showContent()
        
    def showContent(self) -> None:
        self.__canvasForImage.grid(row=0)
        self._title.grid(row=1)
        self._infoMessage.grid(row=2)
        if not self.__errorHasOccured:
            self.__startButton.grid(row=3)
        else:
            self.__quitButton.grid(row=3)


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
        self.__timeoutLabel = tk.Label(self, font=(FONT, 12), 
                                       text="",
                                       fg=BLUE)
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
        # self.showFeedback("All inputs are valid!\n", GREEN)
        feedbackString = ""
        for i, statusLabel in enumerate(self.__statuses):
            if isinstance(allStatuses[i], bool):
                status = allStatuses[i]
            else:
                status = allStatuses[i][0]
            if status:
                statusLabel.setStatus(True)
            else:
                statusLabel.setStatus(False)
                self.__allValid = False
                if i == 0:
                    feedbackString += "There is no input from the camera\n"
                elif i == 1:
                    feedbackString += "The car cannot be seen by the camera\n"
                elif i == 2:
                    tempStr = f"Not all track locations can be found by the camera:\n {allStatuses[2][1]} / {NUM_TRACK_LOCATIONS} found\n"
                    feedbackString += tempStr
                elif i == 3:
                    tempStr = f"Not all hall sensors gave an input:\n {allStatuses[3][1]} / {NUM_HALL_SENSORS} found\n"
                    feedbackString += tempStr
                    
        if self.__allValid:
            self.showFeedback("All inputs are valid!\n", GREEN)       
        else:
            self.showFeedback(feedbackString+"Please do the necessary fixes",
                              RED)
        
    def showContent(self) -> None:
        self._title.grid(row=0, columnspan=2)
        self._infoMessage.grid(row=1, columnspan=2)
        for i, statusLabel in enumerate(self.__statuses):
            statusLabel.grid(i+2)
        curRow = len(self.__statuses)+3
        self.__feedbackLabel.grid(row=curRow, columnspan=2)
        curRow += 1
        self.__timeoutLabel.grid(row=curRow, columnspan=2)
        curRow += 1
        if self.__allValid:
            self.__startTrainingButton.grid(row=curRow, columnspan=2)
        else:
            self.__retryButton.grid(row=curRow, columnspan=2)
            
    def showFeedback(self, feedbackString, colour):
        self.__feedbackLabel.config(text=feedbackString,
                                    fg=colour)
        
    def updateTimoutAfter(self, timeLeft):
        if timeLeft == EMPTY:
            self.__timeoutLabel.config(text="")
        else:
            self.__timeoutLabel.config(text="Timeout After: "+timeLeft+"\n")
        
      
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
                

class FormulAI:
    def __init__(self, master: tk.Tk) -> None:
        # User Interface
        self.__master = master
        self.__master.minsize(width=WINDOW_SIZE[0],
                              height=WINDOW_SIZE[1])
        self.__master.title("FormulAI")
        
        self.__startFrame = StartFrame(self.__master, self.__changeToNextFrame)
        self.__validationFrame = ValidationFrame(self.__master, self.__changeToNextFrame, self.__doValidationRoutine)
        self.__trainingFrame = TrainingFrame(self.__master, self.__changeToNextFrame, self.__stopTraining)
        
        self.__currentFrame = self.__startFrame
        
        # Initializing Modules
        try:
            self.__camera = CameraInput(GREEN_RANGE,
                                        ORANGE_RANGE,
                                        DESLOT_THRESHOLD,
                                        SAMPLE_ITERATIONS)
            self.__hardwareController = HardwareController(DISTANCE_BETWEEN_MAGNETS)
        except ValueError:
            self.__startFrame.raiseError("ValueError: Camera Module Failed to start")
        except serial.serialutil.SerialException:
            self.__startFrame.raiseError("serial.serialutil.SerialException: the serial port is not connected")
        
    def __changeToNextFrame(self) -> None:
        if self.__currentFrame == self.__startFrame:
            self.__currentFrame.delete()
            self.__currentFrame = self.__validationFrame
            self.__doValidationRoutine()
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
        
    def __validateCameraInputs(self):
        self.__statuses[0] = self.__camera.checkCameraIsConnected()
        if self.__statuses[0]:
            self.__statuses[1], cameraLocsFound = self.__camera.checkCarAndTrackLocationsFound(NUM_TRACK_LOCATIONS)
            self.__statuses[2] = [(cameraLocsFound == NUM_TRACK_LOCATIONS), cameraLocsFound]
        
    def __validateHallSensors(self):
        startTime = time()
        timeoutAfter = str(TIMEOUT+1)
        self.__hardwareController.clearSensorsPassed()
        self.__hardwareController.startReading()
        while not self.__statuses[3][0] and time()-startTime < TIMEOUT:
            timeLeft = str(TIMEOUT - int(time()-startTime))
            if timeoutAfter != timeLeft:
                timeoutAfter = timeLeft
                self.__validationFrame.updateTimoutAfter(timeoutAfter)
            numHallSensorsFound = self.__hardwareController.getNumHallInputs()
            self.__statuses[3] = [(numHallSensorsFound == NUM_HALL_SENSORS), numHallSensorsFound]
        self.__hardwareController.stopReading()
        
    def __validateAllInputs(self):
        self.__validationFrame.showFeedback("Validation routine executing...\nPlease wait",
                                            BLUE)
        # There are 2 time consuming processes here:
        # 1. taking many images and analysing them
        # 2. waiting until the timout to get hall sensor data
        # I'm using the current thread for process 1
        # I'm using another thread for process 2, so they can happen near-simultaneously
        hallInputThread = Thread(target=self.__validateHallSensors)
        
        hallInputThread.start()# starting this first, as it is likely to take longer
        self.__validateCameraInputs()
        hallInputThread.join() # waiting for process 2 to terminate before updating statuses
        self.__validationFrame.updateTimoutAfter(EMPTY)
        self.__validationFrame.setStatuses(self.__statuses)
        self.showCurrentFrame()
        
    def __doValidationRoutine(self) -> None: # IMPROVE: maybe make all one target for thread
        self.showCurrentFrame()
        self.__statuses = [False, False, [False, 0], [False, 0]]
        # Threading is required as the routine takes a while to complete.
        # Without threading, the GUI would freeze and be unusable until the routine terminates
        Thread(target=self.__validateAllInputs).start()
        
        
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
    app = FormulAI(root)
    app.showCurrentFrame()
    root.mainloop()