import numpy as np
from random import choice


class QTable:
    def __init__(self, stateShape: list, actionShape: list) -> None:
        self.__stateShape, self.__actionShape = self.__validateShape(stateShape, actionShape)
        if self.__stateShape == self.__actionShape == []:
            raise ValueError("QTable", "State or Action shape is invalid")
        
        # for clarity: will be implemented with list comprehension later
        # iterations per catagory is needed to have O(1) lookup times instead of linear
        self.__stateIterationsPerCatagory = []
        for i in range(3):
            lowerBound = self.__stateShape[0][i]
            upperBound = self.__stateShape[1][i]
            incrementer = self.__stateShape[2][i]
            numIters = len(range(lowerBound, upperBound, incrementer))
            self.__stateIterationsPerCatagory.append(numIters)
        
        # store all the possible states and actions
        self.__allStates = self.__getallStatesFromShape(self.__stateShape)
        self.__allActions = [str(x) for x in range(self.__actionShape[0], # lowerbound
                                                   self.__actionShape[1]+1, # upperbound+1
                                                   self.__actionShape[2])] # incrementer
        
        self.__numCols = len(self.__allStates)
        self.__numRows = len(self.__allActions)
        self.__data = np.zeros((self.__numRows, self.__numCols), dtype=np.float64)

        
    @staticmethod
    def __validateShape(stateShape: list, actionShape: list) -> tuple:
        validLength = 3
        if len(stateShape) == len(actionShape) == validLength:
            for i in range(validLength):
                #validate inner list length to 3
                if len(stateShape[i]) != validLength:
                    print(f"innner list not valid length: {stateShape[i]}")
                    return [], []
                # test for integers input
                try:
                    # state validation
                    for j in range(validLength):
                        stateShape[i][j] = int(stateShape[i][j])
                    # action validation
                    actionShape[i] = int(actionShape[i])
                except ValueError:
                    print(f"invalid inputs: must be int:\n {stateShape}\n {actionShape}\n")
                    return [], []
            for i in range(validLength):
                # test for lower/upper bounds and increments
                if stateShape[0][i] >= stateShape[1][i]:
                    print("lower bound cannot be equal to or bigger than upper bound:")
                    print(f"{stateShape[0][i]} VS {stateShape[1][i]}")
                    return [], []
                elif stateShape[2][i] <= 0:
                    print(f"incrementer must be larger than 0 {stateShape[2][i]}")
                    return [], []
                elif stateShape[2][i] > stateShape[1][i]:
                    print("incrementer cannot be bigger than the upper bound:")
                    print(f"{stateShape[2][i]} > {stateShape[2][i]}")
                    return [], []
            return stateShape, actionShape
        return [], []
                                        
    @staticmethod
    def __getallStatesFromShape(shape: list) -> list:
        states = []
        for s in range(shape[0][0], shape[1][0]+1, shape[2][0]):
            for d in range(shape[0][1], shape[1][1]+1, shape[2][1]):
                for v in range(shape[0][2], shape[1][2]+1, shape[2][2]):
                    states.append(f"{s}{d:02d}{v:03d}")
        return states
    
    def checkStateIsValid(self, state: str) -> bool: 
        if not self.__stateShape[0][0] <= int(state[0]) <= self.__stateShape[1][0]:
            return False
        elif not self.__stateShape[0][1] <= int(state[1:3]) <= self.__stateShape[1][1]:
            return False
        elif not self.__stateShape[0][2] <= int(state[-3:]) <= self.__stateShape[1][2]:
            return False
        else:
            return True
    
    def __stateToIndex(self, state: str) -> int:
        index = 0
        s = (int(state[0]) - self.__stateShape[0][0]) // self.__stateShape[2][0]
        index += s * self.__stateIterationsPerCatagory[1] * self.__stateIterationsPerCatagory[2]
        d = (int(state[1:3]) - self.__stateShape[0][1]) // self.__stateShape[2][1]
        index += d * self.__stateIterationsPerCatagory[2]
        v = (int(state[-3:]) - self.__stateShape[0][2]) // self.__stateShape[2][2]
        index += v 
        # print(state, "->", self.__allStates[index])
        return index
        
    def __actionToIndex(self, action: str) -> int:
        index = (int(action) - self.__actionShape[0]) // self.__actionShape[2]
        # print(action, "->", self.__allActions[index])
        return index
    
    def updateAt(self, state: str, action: str, value: float) -> None:
        row = self.__actionToIndex(action)
        col = self.__stateToIndex(state)
        self.__data[row, col] = value 
    
    def getQValue(self, state: str, action: str) -> float:
        return self.__data[self.__actionToIndex(action),
                           self.__stateToIndex(state)]
    
    def getActionWithMaxQValue(self, state: str) -> str:
        col = self.__stateToIndex(state)
        index = self.__data.argmax(axis=0)[col]
        return self.__allActions[index]
    
    def getMaxQValueOfState(self, state: str) -> float:
        col = self.__stateToIndex(state)
        return np.amax(self.__data, axis=0)[col]
        
    def getRandomAction(self) -> str:
        return choice(self.__allActions)

    def writeQTableToFile(self) -> None:
        with open("QTable.txt", "w") as f:
            f.write("   |  "+",   ".join(self.__allStates))
            f.write("\n---"+"--------"*len(self.__allStates))
            for i, action in enumerate(self.__allActions):
                formatted = []
                for col in self.__data[i]:
                    if col >= 0:
                        formatted.append(f"{col:.2E}")
                    else:
                        formatted.append(f"{col:.1E}")
                        
                f.write(f"\n{action} | "+"  ".join(formatted))
                
                
    def randomise(self):
        from random import random
        for row in range(len(self.__data)):
            for col in range(len(self.__data[row])):
                self.__data[row, col] = random()
                
                
from QTable import QTable
from random import random

class QAgent:
    def __init__(self, params):
        self.__LEARNING_RATE = params["learningRate"]                   # doesnt change throughout training
        self.__DISCOUNT_FACTOR = params["discountFactor"]               # ^
        self.__probabilityToExplore = params["probabilityToExplore"]    # decreases throughout training
        
        self.__totalReward = 0.0
        self.__successfulTrainingIterations = 0
        
        self.__qTable = QTable(params["stateShape"],
                               params["actionShape"])
        
    def __calcNewQValue(self, curState: str, nextState:str, action: str, instantReward: float) -> float:
        oldValue = (1-self.__LEARNING_RATE) * self.__qTable.getQValue(curState, action)
        discountedOptimalFutureReward = self.__DISCOUNT_FACTOR * self.__qTable.getMaxQValueOfState(nextState)
        learnedValue = instantReward + discountedOptimalFutureReward
        newQValue = oldValue + (self.__LEARNING_RATE * learnedValue)
        return newQValue  
    
    def __updateQTable(self, curState: str, action: str, newQValue: float) -> None:
        self.__qTable.updateAt(curState, action, newQValue)  
        
    def __reduceProbToExplore(self) -> None:
        self.__probabilityToExplore *= 0.99    
        
    def decideAction(self, state: str) -> str:
        if not self.__qTable.checkStateIsValid(state):
            return None
        if random() < self.__probabilityToExplore:
            return self.__qTable.getRandomAction()
        else:
            return self.__qTable.getActionWithMaxQValue(state)
    
    def calcInstantReward(self, speed: float, lapsCompleted: int, carHasDeslotted: bool) -> float: 
        if carHasDeslotted:
            return - 1000
        return (speed*0.1) + (lapsCompleted*10) 

    def train(self, curState: str, nextState: str, action: str, instantReward: float) -> bool:
        if not (self.__qTable.checkStateIsValid(curState) and 
                self.__qTable.checkStateIsValid(nextState)):
            return False
        
        newQValue = self.__calcNewQValue(curState, nextState, action, instantReward)
        self.__updateQTable(curState, action, newQValue)
        
        self.__successfulTrainingIterations += 1
        self.__reduceProbToExplore()
        return True

    def writeTable(self) -> None:
        self.__qTable.writeQTableToFile()
       
    
        
    
        
    
    
    
    


if __name__ == '__main__':
    
    # TEST 1: bad length
    # errorTest1 = QTable([[0, 0, 0], [4, 4, 2], [1, 2]],
    #                     [0, 0, 0])
    
    # # TEST 2: bad inputs: strings
    # errorTest2 = QTable([["lower", "zero", "0"], ["upper", "fifty", "50"], ["increment", "one", "1"]],
    #                     ["smallaction", "bigaction", "icrementer"])
    
    # # TEST 3: lowerbound >= upperbound
    # errorTest3 = QTable([[50, 0, 0], [40, 0, 0], [1,1,1]],
    #                     [0, 0, 1])
    
    # # TEST 4: incrementer > 0
    # errorTest4 = QTable([[0, 0, 0], [4, 5, 6], [0, 0, 0]],
    #                     [0, 40, 0])
    
    # TEST 5: incrementer > upper bound
    # errorTest5 = QTable([[0, 0, 0], [4, 4, 4], [4, 5, 6]],
    #                     [0, 40, 40])
    
    # TEST 6: working table
    test6Table = QTable([[0, 2, 0], [1, 6, 4], [1, 2, 1]],
                        [10, 30, 5])
    test6Table.randomise()
    test6Table.writeQTableToFile()
    
    # TEST 7:
    print(test6Table.getQValue("003003", "17"))
    
    # TEST 8:
    print(test6Table.getMaxQValueOfState("003003"))
    
    # TEST 9:
    print(test6Table.getActionWithMaxQValue("003003"))
    
    # TEST 10:
    for i in range(3):
        print(test6Table.getRandomAction())
    
    # TEST 11:
    print("before: ", test6Table.getQValue("003003", "15"))
    test6Table.updateAt("003003", "20", 0.345)
    print("after: ", test6Table.getQValue("003003", "15"))
    
    
    
    #             #  Lower Bounds     Upper Bounds     Increment for each
    # stateShape = [[0, 0, 0],       [1, 99, 999],     [1, 30, 100]]     #    [[0, 40, 0],       [1, 99, 999],     [1, 30, 300]]
    # actionShape = [30,               90,               5]
    
    # qtable = QTable(stateShape, actionShape)
    # qtable.randomize()
    
    # # qtable.stateToIndex("169337")
    
    # # for i in range(5):
    # #     rs = "{:06d}".format(randint(int("040000"), int("199999")))
    # #     print("random state: ", rs)
    # #     print("action w max Q: ", qtable.getActionWithMaxQValue(rs))
    # # qtable.updateAt("023423", "67", 69.69)
    # print(qtable.getMaxQValueOfState("169337"))
    # qtable.writeQTableToFile()
    
    # # qtable.stateToIndex("166345")
    
    
    # # Desision not to use mapping/ to use mapping
    # # check shape is 0-00-000
    