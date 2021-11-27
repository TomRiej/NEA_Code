from Constants import *
from UserInterfaceComponents import *
from Camera import *
from QAgent import *
from Hardware import *

import tkinter as tk
from serial.serialutil import SerialException
from time import time
from threading import Thread

class FormulAI:
    def __init__(self, master: tk.Tk) -> None:
        """The constructor for my main module. Initializes all the other modules and formats the
    	User interface.

        Args:
            master (tk.Tk): the tkinter GUI's root window
        """
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
        try:
            self.__camera = CameraInput()
            self.__qAgent = QAgent()
            self.__hardware = HardwareController()
            self.__master.after(SMALL_TIME_DELAY, self.__hardware.stopCar)
            
        except ValueError as error:
            self.__startFrame.raiseError(f"{error.args[0]} Error: {error.args[1]}")
            
        except SerialException:
            self.__startFrame.raiseError("SerialException: The serial port is not connected")
            
    # ==================== Public Methods ========================================             
    def changeToNextFrame(self) -> None:
        """This function is called each time the user presses a button that leads them to the 
        next frame. It is responsible for calling functions which do four things:
        1. Deleting the old frame
        2. Setting the next frame as the current frame
        3. Setting up the next frames functionality
        4. calling the fuction that will perform the frames functionality.
        """
        if self.__currentFrame is self.__startFrame:
            self.__currentFrame.delete()
            self.__currentFrame = self.__validationFrame
            self.showCurrentFrame()
            
            self.__setupValidationRoutine()
            self.__master.after(SMALL_TIME_DELAY, self.__doValidationRoutine)
        
        elif self.__currentFrame is self.__validationFrame:
            self.__currentFrame.delete()
            self.__currentFrame = self.__trainingFrame
            self.__outputConsole.showConsole()
            self.showCurrentFrame()
            
            self.__setupTraining()
            self.__master.after(SMALL_TIME_DELAY, self.__resumeTraining)
            
        else:
            self.__endProgram()
            
    def manualDeslot(self, event) -> None:
        """the function that is called everytime the spacebar is pressed to handle manual deslots

        Args:
            event (tk.event): argument automatically passed in when binded to a button (unused)
        """
        if self.__currentFrame is self.__trainingFrame:
            self.__carHasDeslotted = True
            self.__outputConsole.printToConsole("Manual Deslot input:"+
                                                "You say the car has deslotted")
            self.__stopTraining()

    def showCurrentFrame(self) -> None:
            """Using polymorphism to show the frame which is currently active
            """
            self.__currentFrame.pack()
            self.__currentFrame.showContent()
            
    # ==================== Private Methods ========================================
    # ==================== General
    def __endProgram(self) -> None:
        """Checks if there are any active threads that need to be stopped before the
        program can terminate. If it is safe to close, then it closes everything properly
        before destroying the window.
        """
        safeToClose = True
        
        # must use isinstance(): self.__validationFrame could be destroyed so cannot compare
        if isinstance(self.__currentFrame, ValidationFrame):
            if self.__validationRoutineIsActive:
                tk.messagebox.showwarning("Closing Error", "Cannot terminate program, as the "+
                                        "validation thread is still running. "+
                                        "\nPlease wait for the timeout.")
                safeToClose = False
        
        if isinstance(self.__currentFrame, TrainingFrame):
            print("Stopping Training")
            self.__stopTraining()
        
        if safeToClose:
            print("\n\n***** Closing *****\n")
            print("Stopping car...")
            self.__hardware.stopCar()
            print("Closing Serial Ports...")
            self.__hardware.closeSerial()
            print("Releasing Camera Input...")
            self.__camera.close()
            self.__master.destroy()
        
    def __startMovingCar(self, angle: int) -> None:
        """starts the car moving from a stand still. This method is required to overcome static
        friction on the car. It must be defined here as it requires a 350ms delay, which has to
        be done using __master.after() so the GUI doesnt freeze

        Args:
            angle (int): the angle that the car should start to move in
        """
        self.__hardware.setServoAngle(SERVO_RANGE[1])
        self.__master.after(350, self.__hardware.setServoAngle, angle)
                
    # ==================== Validation Routine
    def __doValidationRoutine(self) -> None:
        """starts a thread which will validate all the inputs in the background of the GUI.
        It only opens a thread if the validation routine isn't already active. If it is, it 
        prevents the user from starting a new thread.
        """
        if self.__validationRoutineIsActive:
            tk.messagebox.showwarning("Retry Error", "Couldn't restart the validation routine "+
                                                    "as it is already active. Please wait for "+
                                                    "it to timeout, then retry.")
        else:
            self.__statuses = [False, [False, 0], [False, 0], [False, 0]]
            # Threading required: the routine will take some time and GUI can't freeze
            validationRoutineThread = Thread(target=self.__validateAllInputs)
            validationRoutineThread.start()
    
    def __setupValidationRoutine(self) -> None:
        """performing the necessary operations that need to be done before running the
        validation routine for the first time.
        """
        self.__validationRoutineIsActive = False
        self.__startMovingCar(SLOW_ANGLE)
            
    def __validateAllInputs(self) -> None:
        """Calls the relevant functions that will validate the camera and hall sensors 
        simulateously. It does this by starting a new thread to validate the hall threads, 
        and using the current thread to validate the camera input. After the validation is done,
        it updates the UI to show the results.
        """
        self.__validationRoutineIsActive = True
        self.__validationFrame.showFeedback("Validation routine executing...\nPlease wait", BLUE)
        
        # Creating a new Thread for validating the Hall sensors so both happen near-simulatenously
        hallSensorValidationThread = Thread(target=self.__validateHallSensors)
        hallSensorValidationThread.start()
        
        # Using this Thread for validating the camera
        self.__validateCameraInput()
        
        # wait for hall sensor validation to finish before updating the statuses
        hallSensorValidationThread.join()
        self.__validationFrame.updateTimoutAfter(EMPTY)
        self.__validationFrame.setStatuses(self.__statuses)
        self.__validationRoutineIsActive = False
        self.showCurrentFrame()
            
    def __validateHallSensors(self) -> None:
        """starts reading from hall sensors and validates that the number of hall sensors
        activations is equal to the number of hall sensors on the track. After it either times out,
        or finds all the sensors, it will save the resuts to the statuses list.
        """
        # reset any measurements from before and start to read incoming data
        self.__hardware.resetSensorActivations()
        self.__hardware.startReadingSerial()
        
        # start the timeout counter and show the user
        startTime = time()
        countdownNumberShownToUser = str(VALIDATION_TIMEOUT)
        self.__validationFrame.updateTimoutAfter(countdownNumberShownToUser)
        
        # while all the sensors haven't been found yet and the validation hasn't timed out
        while not self.__statuses[3][0] and time()-startTime < VALIDATION_TIMEOUT:
            # check the hall sensors
            numHallSensorsActivated = self.__hardware.getNumSensorsActivated()
            self.__statuses[3] = [(numHallSensorsActivated == NUM_HALL_SENSORS),
                                  numHallSensorsActivated]
            
            # update timeout countdown for the user only if it's different to what is being shown
            timeLeft = str(VALIDATION_TIMEOUT - int(time() - startTime))
            if timeLeft != countdownNumberShownToUser:
                countdownNumberShownToUser = timeLeft
                self.__validationFrame.updateTimoutAfter(countdownNumberShownToUser)
            
        # after all sensors have been activated or it timed out
        self.__hardware.stopReadingSerial()
        # let the user know this part of the validation is finished
        self.__validationFrame.updateTimoutAfter("complete")
           
    def __validateCameraInput(self) -> None:
        """checks if the camera is connected first. If the camera is connected, continue to 
        validate that the car and track locations can be seen. The results are saved into the
        statuses list. To find the car, I'm finding the number of moving pixels in the frame. This
        allows me to diffentiate between too many moving pixels (other moving things in the frame)
        and too little moving pixels (car can't be found)
        """
        self.__statuses[0] = self.__camera.checkCameraConnected()
        # only perform the rest of the validation if the camera is actually connected
        if self.__statuses[0]:
            nCarPixels, numCameraLocations = self.__camera.countCarPixelsAndTrackLocations()
            self.__statuses[1] = [NUM_CAR_PIXELS_RANGE[0] <= nCarPixels <= NUM_CAR_PIXELS_RANGE[1],
                                  nCarPixels]
            self.__statuses[2] = [numCameraLocations == NUM_TRACK_LOCATIONS,
                                  numCameraLocations]
        
    # ==================== Training
    def __doTrainingLoop(self) -> None: 
        """the is the method that is repeatedly called to train the agent. It performs the entire
        training algorithm by calling all the relevant methods to get states, decide actions,
        calculate rewards, and update the Q table. If anything unexpected goes wrong, it will let
        the user know via the output console. 
        """
        # Update the User Interface
        self.showCurrentFrame()
        self.__updateGraph()
        
        # training iteration
        carStateAndSpeed = self.__getCarStateAndSpeed()
        if carStateAndSpeed is not INVALID:
            initialState, initialSpeed = carStateAndSpeed
            action = self.__qAgent.decideAction(initialState)
            if action is not INVALID:
                self.__hardware.setServoAngle(int(action))
                # cannot use time.sleep as it will affect the GUI
                startTime = time()
                while time() - startTime < WAITING_TIME_FOR_ACTION:
                    # waiting time doing nothing
                    pass
                carStateAndSpeed = self.__getCarStateAndSpeed()
                if carStateAndSpeed is not INVALID:
                    finalState, finalSpeed = carStateAndSpeed
                    reward = self.__qAgent.getUpdatedReward((initialSpeed + finalSpeed) / 2,
                                                            len(self.__lapTimes),
                                                            self.__carHasDeslotted)
                    success = self.__qAgent.train(initialState,
                                                  finalState,
                                                  action,
                                                  reward)
                    if success:
                        self.__outputConsole.printToConsole("Trained:\n"+
                            f"Training Iteration: {self.__qAgent.getNumTrainingIterations()}\n"+
                            f"P(Explore): {self.__qAgent.getProbabilityToExplore()}\n"+
                            f"Initial State: {initialState}\n"+
                            f"Action Chosen: {action}\n"+
                            f"Final State: {finalState}\n"+
                            f"Deslotted: {self.__carHasDeslotted}\n"+
                            f"Total Reward: {reward}\n\n")
                    else:
                        self.__outputConsole.printToConsole("Failed to train: Initial Or Final "+
                                                            "state was invalid when training")
                else:
                    self.__outputConsole.printToConsole("Failed to train: Couldn't get final "+
                        "state as camera speed was not in range of hall sensor speed or the "+
                        "camera is not working")
            else:
                self.__outputConsole.printToConsole("Failed to train: Action could not be "+
                    "decided as the initial state was invalid")
        else:
            self.__outputConsole.printToConsole("Failed to train: Couldn't get initial state "+
                "as camera speed was not in range of hall sensor speed or the camera is "+
                "not working")
        
        # loop
        if self.__contineTraining and not self.__carHasDeslotted:
            self.__master.after(REFRESH_AFTER, self.__doTrainingLoop)
        else:
            self.__outputConsole.printToConsole("Training stopped")
            self.__hardware.stopCar()
    
    def __getCarStateAndSpeed(self) -> tuple:
        """uses the camera info to get new information on the car. It tries to validate the speed
        using the hall sensor values. It then formats the information into a 6 digit state string.
        it returns both the state, and the speed, so that the speed can be used to calculate reward.

        Returns:
            tuple: the state and the speed (millimeters per second)
        """
        carInfo = self.__camera.getCarInfo()
        if carInfo is INVALID:
            return INVALID
        
        validatedCarSpeed = self.__getValidatedCarSpeed(carInfo)
        if validatedCarSpeed is INVALID:
            return INVALID
        
        # formatting the state 0-00-000
        severity = str(carInfo["nextTrackLocationType"])
        # rounding distance to nearest cm -> 2 digit number
        distance = "{:02d}".format(int((carInfo["nextTrackLocationDistanceMillimeters"]+5)/10))
        # rounding speed to nearest cm/s -> 3 digit number
        speed = "{:03d}".format(int((carInfo["speed"]+5)/10))
        return f"{severity}{distance}{speed}", carInfo["speed"]
    
    def __getValidatedCarSpeed(self, cameraInfo: dict) -> float:
        """tries to validate the camera speed against the hall sensor speed if their measurements
        were taken at near the same time. 

        Args:
            cameraInfo (dict): the full dictionary with the cars information

        Returns:
            float: returns the average speed of the hall sensors and camera if possible, 
                    otherwise, just the camera speed.
        """
        hallSensorInfo = self.__hardware.getCarInfo()
        if hallSensorInfo is EMPTY:
            return cameraInfo["speed"]
        
        timeBetweenMeasurements = abs(cameraInfo["timeOfMeasurement"] 
                                      - hallSensorInfo["timeOfMeasurement"])
        if timeBetweenMeasurements < MAX_TIME_BETWEEN_MEASUREMENTS:
            cameraSpeed = cameraInfo["speed"]
            hallSpeed = hallSensorInfo["speed"]
            self.__outputConsole.printToConsole(f"comparing: hall:{hallSpeed}"+
                                                f"vs camera:{cameraSpeed}")
            if (cameraSpeed < hallSpeed-HALL_VS_CAMERA_SPEED_TOLERANCE or 
                cameraSpeed > hallSpeed+HALL_VS_CAMERA_SPEED_TOLERANCE):
                return INVALID
            return (cameraSpeed + hallSpeed) / 2
        return cameraInfo["speed"]
    
    def __resumeTraining(self) -> None:
        """the method that will reset all the values required for the training loop, then start
        the training loop.
        """
        self.__outputConsole.printToConsole("Training resumed")
        self.__contineTraining = True
        self.__carHasDeslotted = False
        self.__lapTimes = []
        self.__trainingFrame.showStopButton()
        self.__hardware.resetSensorActivations()
        self.__hardware.startReadingSerial()
        self.__startMovingCar(SLOW_ANGLE)
        # create a new thread for the training loop as it requires waiting time for actions
        self.__trainingLoopThread = Thread(target=self.__doTrainingLoop)
        self.__master.after(SMALL_TIME_DELAY, self.__trainingLoopThread.start)
         
    def __setupTraining(self) -> None:
        """perform the necessary operations that need to be done before running the training loop 
        for the first time.
        """
        self.__hardware.stopCar()
        self.__hardware.startMeasuringLapTimes()
    
    def __stopTraining(self) -> None:
        """performs the necessary operations to stop the training loop.
        """
        self.__contineTraining = False
        self.__trainingLoopThread.join()
        self.__hardware.stopReadingSerial()
        self.__hardware.stopCar()
        self.__trainingFrame.showResumeButton()
        
    def __updateGraph(self) -> None:
        """checks if there is a new laptime available from the hardware module. If there is a new
        laptime, it will call the relevant functions to update the UI graph with the new info.
        """
        newLapTime = self.__hardware.getNewLapTime()
        if newLapTime is not EMPTY:
            self.__lapTimes.append(newLapTime)
            self.__trainingFrame.updateGraph(self.__lapTimes)
        

if __name__ == '__main__':
    root = tk.Tk()
    app = FormulAI(root)
    app.showCurrentFrame()
    root.mainloop()
