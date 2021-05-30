from QTable import QTable
from random import random


DEBUG = False

class QAgent:
    def __init__(self, **kwargs) -> None:
        self.__learningRate = kwargs["learningRate"]
        self.__discountFactor = kwargs["discountFactor"]
        self.__probabilityToExplore = kwargs["probabilityToExplore"]
        
        self.__SPEED_TO_REWARD_K = 1 
        
        self.__totalReward = 0.0
        
        self.__qTable = QTable(kwargs["stateRange"],
                             kwargs["actionRange"],
                             kwargs["stateGroupSize"],
                             kwargs["actionGroupSize"])

            
    def decideAction(self, state: int) -> int:
        if random() < self.__probabilityToExplore:
            if DEBUG:
                print("random action chosen")
            return self.__qTable.getRandomAction()
        else:
            if DEBUG:
                print("chose max Qvalue")
            return self.__qTable.getActionWithMaxQValue(state)
        
    def calcNewQValue(self, curState: int, nextState: int, action: int, reward: float) -> float:
        oldValue = (1-self.__learningRate) * self.__qTable.getQValue(curState, action)
        discountedOptimalFutureReward = self.__discountFactor * self.__qTable.getActionWithMaxQValue(nextState)
        learnedValue = reward + discountedOptimalFutureReward
        newQvalue = oldValue + (self.__learningRate * learnedValue)
        if DEBUG:
            print(f"old Value: {oldValue} dicOptFut: {discountedOptimalFutureReward} learned: {learnedValue}")
            print(f"New Q value: {newQvalue}")
        return newQvalue
    
    def updateQValue(self, state: int, action: int, value: float) -> None:
        self.__qTable.update(state, action, value)
        

    def calcReward(self, speed: int, carHasDeslotted: bool) -> float: # Reward function
        instReward = 0.0
        if carHasDeslotted:
            self.__totalReward * 0.5
            instReward = -1000.0
        else:
            instReward = self.__speedToReward(speed)
        return instReward
            
    def __speedToReward(self, speed: int) -> float:
        return speed*self.__SPEED_TO_REWARD_K
    
    def printQTable(self):
        self.__qTable.printTable()
            
    
    
params = {"stateRange": [0,5],
          "actionRange": [0,5],
          "stateGroupSize": 1,
          "actionGroupSize": 1,
          "learningRate": 0.95,  # how much of the new value it retains
          "discountFactor": 0.05,# how much future rewards will influence the Qvalue
          "probabilityToExplore": 0.1}



# Test:        
# possible States: 0-5
# possible Actions: 0-5
# speed = reward for this test case. 
if __name__ == '__main__':
    agent = QAgent(**params)

    state1 = 0
    speed = 0

    for i in range(10000): # Training loop
        deslotted = False
        action = agent.decideAction(state1)
        speed = action    

        # I could punish the car for standing still, but it would learn that taking other
        # options should result in a higher result, so punishing it isnt neccesary
        
        if random() < state1/20:     # lower state (lower speeds) has less chance of deslotting
            if random() < action/20: # lower speed chosen = lower chance of deslotting
                deslotted = True     # The car should learn that higher speeds are risky
            
            
        instantReward = agent.calcReward(speed, deslotted)
        
        if DEBUG:
            print(f"iteration {i} with state {state1}")    
            print(f"action: {action}")
            print(f"reward = {instantReward}")
        
        # change the speed based off the action chosen
        if action == 0:
            state2 = 0
        elif action >= state1 and state1 < 5: # increase the state if a high speed is chosen
            state2 = state1 + 1 
        elif action <= state1 and state1 > 0: # decrease the state if a low speed is chosen
            state2 = state1 - 1
            
        newQvalue = agent.calcNewQValue(state1, state2, action, instantReward)
        agent.updateQValue(state1, action, newQvalue)
        
        state1 = state2 
        
    agent.printQTable()   
        
    
    
        
    
