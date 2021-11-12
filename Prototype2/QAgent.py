from Constants import *
from QTable import *

from random import random


class QAgent:
    def __init__(self) -> None:
        # any arbitrary starting reward should work
        self.__totalReward = 2000.0
        
        self.__successfulTrainingIterations = 0
        
        if not MAX_EXPLORING_ITERATIONS > 0:
            # division by 0 error preventing
            raise ValueError("QAgent", "MAX_EXPLORING_ITERATIONS must be > 0")
        self.__updateProbabilityToExplore()
        
        self.__qTable = QTable()
        
    # ==================== Private ======================================== 
    def __calcNewQValue(self, currentState:str, nextState:str, action:str, reward:float) -> float:
        """uses the Q value formula to calculate the new QValue using the states, action
        and reward passed in.

        Args:
            currentState (str): the 6 digit state string the car started in (assumed to be valid)
            nextState (str): the 6 digit state string the car ended in (assumed to be valid)    
            action (str): the action string chosen (guarenteed to be valid)
            reward (float): the reward calculated for the this action

        Returns:
            float: the new Q value
        """
        oldValue = (1-LEARNING_RATE) * self.__qTable.getQValue(currentState, action)
        discountedOptimalFutureReward = DISCOUNT_FACTOR * self.__qTable.getMaxQValue(nextState)
        learnedValue = reward + discountedOptimalFutureReward
        newQValue = oldValue + (LEARNING_RATE * learnedValue)
        return newQValue
        
    def __updateQTable(self, state: str, action: str, newQValue: float) -> None:
        """updates the QTable at the specified location with the specified value

        Args:
            state (str): the 6 digit state string (assumed to be valid)
            action (str): the action string (guaranteed to be valid)
            newQValue (float): the new Q value that needs to be written
        """
        self.__qTable.update(state, action, newQValue)
    
    @staticmethod
    def __getPToExplore(numTrainingIters: int) -> float:
        """function to calculate the probability to explore for a given iteration during the
        training. This method can be modified if this particular function turns out to be 
        unsuitable

        Args:
            numTrainingIters (int): the number of successful training iterations completed

        Returns:
            float: the value between 0 -> 1 for the new P(explore)
        """
        return 0.5 * np.cos((np.pi / MAX_EXPLORING_ITERATIONS) * numTrainingIters) + 0.5
    
    def __updateProbabilityToExplore(self) -> None:
        """Updates the probability to explore based on how many training iterations have been
        completed. Once __successfulTrainingIterations > MAX_EXPLORING_ITERATIONS, the 
        p(explore) is 0, so we dont need to update it.
        """
        if self.__successfulTrainingIterations <= MAX_EXPLORING_ITERATIONS:
            self.__probabilityToExplore = self.__getPToExplore(self.__successfulTrainingIterations)
        
    # ==================== Public ======================================== 
    def decideAction(self, state: str) -> str:
        """using Epsilon greedy action selection to decide an action for the agent to take.
        Depending on probability to explore, the agent takes a random action to 'explore' the 
        environment or choose (what it thinks is) the best action to 'exploit' its knowledge.

        Args:
            state (str): the 6 digit state string (needs to be validated)

        Returns:
            str: the action taken
        """
        if not self.__qTable.validateState(state):
            return INVALID
        
        if random() < self.__probabilityToExplore:
            return self.__qTable.getRandomAction()
        else:
            return self.__qTable.getActionWithMaxQValue(state)
            
    def getUpdatedReward(self, speed: float, lapsCompleted: int, carHasDeslotted: bool) -> float:
        """ The reward function for my QAgent. It calculates the new total reward based on the
        information passed in:
        speed: using the speed (mm/s) to encourage higher speeds
        lapsCompleted: using the number or laps completed without deslotting
        to encourage longer runs. (x10 for higher weighting)
        deslotted: apply a big punishment for a deslot to discourage this.

        Args:
            speed (float): the final speed of the car after taking an action (mm/s)
            lapsCompleted (int): the number of laps completed without deslotting
            carHasDeslotted (bool): if the user said the car has deslotted.

        Returns:
            float: the new total reward which will be used to calculate a new Q value.
        """
        if carHasDeslotted:
            self.__totalReward *= 0.5 
        else:
            self.__totalReward += (speed*0.1) + (lapsCompleted*10)
        return self.__totalReward
    
    def train(self, currentState: str, nextState: str, action: str, reward: float) -> bool:
        # validate states passed in
        if not (self.__qTable.validateState(currentState) and 
                self.__qTable.validateState(nextState)):
            return False
        
        newQValue = self.__calcNewQValue(currentState, nextState, action, reward)
        self.__updateQTable(currentState, action, newQValue)
        self.__successfulTrainingIterations += 1
        self.__updateProbabilityToExplore()
        
        return True
    
    
if __name__ == '__main__':
    q = QAgent()
    # import matplotlib.pyplot as plt
    
    ## exponentials Test 1
    # exps = [1-(1e-2),
    #         1-(1e-3),
    #         1-(1e-4),
    #         1-(1e-5),
    #         1-(1e-6)]
    # colours = ["r", "y", "g", "b", "m"]
    # xs = []
    # ys = []
    
    
    # for i in range(5):
    #     n = exps[i]
    #     pEx = 1
    #     x = []
    #     y = []
    #     for j in range(500000):
    #         x.append(j)
    #         y.append(pEx)
    #         pEx *= n
    #     xs.append(x)
    #     ys.append(y)
        
    # for i in range(5):
    #     plt.plot(xs[i], ys[i], colours[i])
    # plt.show()
    
    ## cos Test 2
    # ITERS = 300
    # def f(x):
    #     if x < ITERS:
    #         return 0.5*np.cos((np.pi/ITERS)*x) + 0.5
    #     else: return 0
    
    # x = []
    # y = []
    # for i in range(500):
    #     x.append(i)
    #     y.append(f(i))
    # plt.plot(x, y)
    # plt.show()
    