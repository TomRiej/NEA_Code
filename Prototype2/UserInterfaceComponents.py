from Constants import *

import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class MyFrame(tk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        """The base frame that all my UI classes should inherit from.
        From inheritance they should get the _title and _infoMessage attributes.

        Args:
            master (tk.Tk): the Tkinter window which this frame is in
        """
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
        
    def raiseError(self, errorMessage: str) -> None:
        """method to display an error message to the user on the TKinter UI

        Args:
            errorMessage (str): the message that needs to be shown to the user
        """
        self.__errorHasOccured = True
        self._infoMessage.config(text="\n   "+errorMessage+"    \n\n",
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
        """A custom class that will enable me to create the status labels how i want

        Args:
            master (tk.Tk): the window that this statuslabel will be in
            infoText (str): the status info: eg 'Car is seen'
        """
        self.__infoText = tk.Label(master,
                                   text=infoText +": ",
                                   font=(FONT, 25))
        self.__statusText = tk.Label(master,
                                     text="Failed",
                                     fg=RED,
                                     font=(FONT, 25))
    
    def setStatus(self, status: bool) -> None:
        """a method to set the status of the label

        Args:
            status (bool): true or false denoting whether the status should be pass / fail
        """
        if status:
            self.__statusText.config(text="Passed",
                                     fg=GREEN)
        else:
            self.__statusText.config(text="Failed",
                                     fg=RED)

    def grid(self, row: int) -> None:
        self.__infoText.grid(row=row, column=0)
        self.__statusText.grid(row=row, column=1)


class ValidationFrame(MyFrame):
    def __init__(self, master: tk.Tk, changeFrameFunc, retryFunc) -> None:
        super().__init__(master)
        self._title.config(text="Validation Screen")
        
        self._infoMessage.config(text=
        """This is the screen where you must make sure all the inputs
        are working as expected.\n""")
        
        # my requirements only require 4 statuses, so i've coded this section specifically to
        # fulfill four requirements only.
        self.__statuses = [StatusLabel(self, "Input from iPhone camera"),
                           StatusLabel(self, "Car is seen by the camera"),
                           StatusLabel(self, "Track is seen by the camera"),
                           StatusLabel(self, "Input from on-track sensors")]
        
        
        self.__feedbackLabel = tk.Label(self, font=(FONT, 15))
        self.showFeedback("Allowing time for the car to start moving\n", BLUE)
        
        self.__timeoutLabel = tk.Label(self, font=(FONT, 12), 
                                       text=EMPTY,
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
        """method that allows me to modify all the statuses according to the list passed in
        coded specifically for 4 statuses only, but could be expanded if needed later.

        Args:
            allStatuses (list): list of all the statuses passed in:
            Format:
            [   bool,
                [bool, Number of moving pixels],
                [bool, Number of Track Locations found],
                [bool, Numner of Hall sensors activated]    ]
        """ 
        self.__allValid = True
        feedbackString = EMPTY
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
                    pixels = allStatuses[i][1]
                    if pixels < NUM_CAR_PIXELS_RANGE[0]:
                        feedbackString += f"Not enough moving pixels to recognise a car:\
                                            {pixels} pixels\n"
                    else:
                        feedbackString += f"Too many moving pixels to recognise a car: \
                                            {pixels} pixels\n"     
                elif i == 2:
                    tempStr = f"Not all track locations can be found by the camera:\n\
                                {allStatuses[2][1]} / {NUM_TRACK_LOCATIONS} found\n"
                    feedbackString += tempStr
                elif i == 3:
                    tempStr = f"Not all hall sensors gave an input:\n\
                                {allStatuses[3][1]} / {NUM_HALL_SENSORS} found\n"
                    feedbackString += tempStr
                    
        if self.__allValid:
            self.showFeedback("All inputs are valid!\n", GREEN)       
        else:
            self.showFeedback(feedbackString+"Please do the necessary fixes",
                              RED)
        
    def updateTimoutAfter(self, info):
        """method to show a timeout countdown if needed

        Args:
            info (str): denotes what should be shown on the label
            "": dont show the label
            "complete":  all sensors found so countdown no longer needed
            "{1-10}": the number of the countdown 
        """
        if info == EMPTY:
            self.__timeoutLabel.config(text=EMPTY)
        elif info == "complete":
            self.__timeoutLabel.config(text="Found all hall sensors\nWaiting for the camera")
        else:
            self.__timeoutLabel.config(text="Timeout After: "+info+"\n")

    def showFeedback(self, feedbackString: str, colour: str):
        """method to modify the label showing the user's feedback

        Args:
            feedbackString (str): the feedback that needs to be given
            colour (str): the colour of the font in Hex. RBG format eg #FFFFFF
        """
        self.__feedbackLabel.config(text=feedbackString,
                                    fg=colour)
        
    def showContent(self) -> None:
        self._title.grid(row=0, columnspan=2)
        self._infoMessage.grid(row=1, columnspan=2)
        for i, statusLabel in enumerate(self.__statuses):
            statusLabel.grid(i+2)
        # row numbers can be hardcoded as I'm only using 4 statuses as per my requirements
        self.__feedbackLabel.grid(row=6, columnspan=2)
        self.__timeoutLabel.grid(row=7, columnspan=2)
        if self.__allValid:
            self.__startTrainingButton.grid(row=8, columnspan=2)
        else:
            self.__retryButton.grid(row=8, columnspan=2)


class TrainingFrame(MyFrame):
    def __init__(self, master: tk.Tk, endFunc, stopLoopFunc, resumeFunc) -> None:
        super().__init__(master)
        self._title.config(text="Training Screen")
        
        self._infoMessage.config(text=
    """This is the screen which shows you the progress of the Reinforcement
    learning algorithm that is being applied to the car.""")
        
        self.__stopFunc = stopLoopFunc
        self.__resumeFunc = resumeFunc
        self.__stopAndResumeButton = tk.Button(self,
                                      height=2,
                                      width=15,
                                      text="STOP",
                                      fg=RED,
                                      font=(FONT, 25),
                                      command=self.__stopFunc)
                
        self.__endProgramButton = tk.Button(self,
                                               height=2,
                                               width=15,
                                               text="End Program",
                                               font=(FONT, 25),
                                               command=endFunc)
        # setting up the graphs
        # I'm using both:
        # https://www.geeksforgeeks.org/how-to-embed-matplotlib-charts-in-tkinter-gui/
        # https://pythonprogramming.net/embedding-live-matplotlib-graph-tkinter-gui/
        # to help me embed the graph into the window
        self.__fig = plt.Figure(figsize=(3,3), dpi=100)
        self.__fig.set_tight_layout(True)
        self.__myPlot = self.__fig.add_subplot(111)
        self.__canvasGraph = None
        
    def showStopButton(self):
        self.__stopAndResumeButton.config(text="STOP",
                                          fg=RED,
                                          command=self.__stopFunc)
        
    def showResumeButton(self):
        self.__stopAndResumeButton.config(text="Resume",
                                          fg=GREEN,
                                          command=self.__resumeFunc)
        
    def updateGraph(self, newData: list) -> None: # REFINE
        """method to render the graph into a Tkinter compatible format

        Args:
            newData (list): list of tuples eg:
            [(1, 3.4), (2, 3.5), (3, 4.3)]
        """
        xList = []
        yList = []
        for x, y in newData:
            xList.append(x)
            yList.append(y)
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
        self.__stopAndResumeButton.grid(row=3, column=0, columnspan=1)
        self.__endProgramButton.grid(row=3, column=1, columnspan=1)


class OutputConsole(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master,
                             width=WINDOW_SIZE[0],
                             height=WINDOW_SIZE[0],
                             bg=BG_COLOUR)
        self.__master = master
        self.title("Output Console")
        # iconify hides the window when i dont need it
        self.iconify()
        
        self.__outputText = EMPTY
        self.__outputTextArea = tk.Text(self,
                                        bg=BG_COLOUR,
                                        yscrollcommand=True,
                                        # disabling the text area so the user cant type there.
                                        state="disabled")

        self.printToConsole("This console shows you what the program is doing")
        
        
    def showConsole(self):
        # display this window to the right of the main window with 20 pixels padding
        x = self.__master.winfo_x() + WINDOW_SIZE[0] + 20
        y = self.__master.winfo_y()
        self.geometry(f"+{x}+{y}")
        # deiconify shows the window
        self.deiconify()
        # transient means this window moves with the main window if the main window is moved
        self.transient(self.__master)
        self.__outputTextArea.pack(expand=True, fill="both")
        
    def printToConsole(self, text):
        if DEBUG:
            print(text)
        # we need to activate the window before we can add text to it
        self.__outputTextArea.config(state="normal")
        self.__outputTextArea.insert("end", self.__outputText + f": {text}\n")
        self.__outputTextArea.config(state="disabled")
        # automatically scroll the textArea to the bottom where the most recent message is printed
        self.__outputTextArea.see("end")