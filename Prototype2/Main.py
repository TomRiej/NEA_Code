from Constants import *
from UserInterfaceComponents import *

import tkinter as tk


class FormulAI:
    def __init__(self, master: tk.Tk) -> None:
        self.__master = master
        
        # formatting the window
        self.__master.minsize(width=WINDOW_SIZE[0],
                              height=WINDOW_SIZE[1])
        self.__master.title("FormulAI")
        self.__master.tk_setPalette(background=BG_COLOUR)
        # Thread exception handling in endProgram
        self.__master.protocol("WM_DELETE_WINDOW", self.__endProgram) 
        self.__master.bind("<space>", self.manualDeslot)
        self.__outputConsole = OutputConsole(master)
        
        # initializing the 3 frames
        self.__startFrame = StartFrame(self.__master, 
                                       self.changeToNextFrame)
        self.__validationFrame = ValidationFrame(self.__master, 
                                                 self.changeToNextFrame, 
                                                 self.__doValidationRoutine)
        self.__trainingFrame = TrainingFrame(self.__master, 
                                             self.changeToNextFrame, 
                                             self.__stopTraining, 
                                             self.__resumeTraining)
        
        self.__currentFrame = self.__startFrame
        
        # initializing my other Modules
        pass
    
    # ==================== Public Methods ========================================             
    def showCurrentFrame(self) -> None:
        self.__currentFrame.pack()
        # polymorphism
        self.__currentFrame.showContent()
        
    def changeToNextFrame(self) -> None:
        if self.__currentFrame == self.__startFrame:
            # change the UI frame
            self.__currentFrame.delete()
            self.__currentFrame = self.__validationFrame
            self.showCurrentFrame()
            
            # set up for validation
        
        elif self.__currentFrame == self.__validationFrame:
            # change the UI frame
            self.__currentFrame.delete()
            self.__currentFrame = self.__trainingFrame
            self.__outputConsole.showConsole()
            self.showCurrentFrame()
            
            # set up for training
            
        else:
            self.__endProgram()
            
    def manualDeslot(self, event) -> None:
        if self.__currentFrame == self.__trainingFrame:
            # self.__carHasDeslotted = True
            self.__outputConsole.printToConsole("Manual Deslot input:"+
                                                "You say the car has deslotted")
            



    # ==================== Private Methods ========================================
    # ==================== General
    def __endProgram(self) -> None:
        self.__master.destroy()
        
    # ==================== Validation Routine
    def __doValidationRoutine(self) -> None:
        self.showCurrentFrame()
        self.__validationFrame.setStatuses([True for x in range(4)])
        

        
        
        
        
        
        
        
        
        
        

if __name__ == '__main__':
    root = tk.Tk()
    app = FormulAI(root)
    app.showCurrentFrame()
    root.mainloop()
