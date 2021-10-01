import numpy as np
from random import random, choice


class QTable:
    def __init__(self, stateShape, actionShape) -> None:
        self.__stateShape, self.__actionShape = self.__validateShape(stateShape, actionShape)
        if self.__stateShape == self.__actionShape == []:
            raise ValueError("QTable", "State or Action shape is invalid")
        
        self.__stateIterationsPerCatagory = [len(range(self.__stateShape[0][x], self.__stateShape[1][x], self.__stateShape[2][x])) for x in range(3)]
        
        self.__allStates = self.__getallStatesFromShape(self.__stateShape)
        self.__allActions = [str(x) for x in range(self.__actionShape[0],
                                                   self.__actionShape[1]+1, 
                                                   self.__actionShape[2])]
        
        self.__numCols = len(self.__allStates)
        self.__numRows = len(self.__allActions)
        self.__data = np.zeros((self.__numRows, self.__numCols), dtype=np.float64)
        np.set_printoptions(precision=3, suppress=True, linewidth=120) # just to make to output look decent
        
    @staticmethod
    def __validateShape(stateShape, actionShape):
        validLength = 3
        if len(stateShape) == len(actionShape) == validLength:
            for i in range(validLength):
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
                    print(f"lower bound cannot be equal to or bigger than upper bound:\n{stateShape[0][i]} VS {stateShape[1][i]}")
                    return [], []
                elif stateShape[2][i] <= 0:
                    print(f"incrementer must be larger than 0 {stateShape[2][i]}")
                    return [], []
                elif stateShape[2][i] > stateShape[1][i]:
                    print(f"incrementer cannot be bigger than the upper bound:\n{stateShape[2][i]} > {stateShape[2][i]}")
                    return [], []
            return stateShape, actionShape
        return [], []
                                        
    @staticmethod
    def __getallStatesFromShape(shape):
        states = []
        for s in range(shape[0][0], shape[1][0]+1, shape[2][0]):
            for d in range(shape[0][1], shape[1][1]+1, shape[2][1]):
                for v in range(shape[0][2], shape[1][2]+1, shape[2][2]):
                    states.append(f"{s}{d:02d}{v:03d}")
        return states
    
    def checkStateIsValid(self, state): 
        if not self.__stateShape[0][0] <= int(state[0]) <= self.__stateShape[1][0]:
            return False
        elif not self.__stateShape[0][1] <= int(state[1:3]) <= self.__stateShape[1][1]:
            return False
        elif not self.__stateShape[0][2] <= int(state[-3:]) <= self.__stateShape[1][2]:
            return False
        else:
            return True
    
    def checkActionIsValid(self, action): # needed?
        if not self.__actionShape[0] <= int(action) <= self.__actionShape[1]:
            return False
        else:
            return True
    
    def __stateToIndex(self, state):
        index = 0
        s = (int(state[0]) - self.__stateShape[0][0]) // self.__stateShape[2][0]
        index += s * self.__stateIterationsPerCatagory[1] * self.__stateIterationsPerCatagory[2]
        d = (int(state[1:3]) - self.__stateShape[0][1]) // self.__stateShape[2][1]
        index += d * self.__stateIterationsPerCatagory[2]
        v = (int(state[-3:]) - self.__stateShape[0][2]) // self.__stateShape[2][2]
        index += v 
        # print(state, "->", self.__allStates[index])
        return index
        
    def __actionToIndex(self, action):
        index = (int(action) - self.__actionShape[0]) // self.__actionShape[2]
        # print(action, "->", self.__allActions[index])
        return index
    
    def updateAt(self, state, action, value):
        row = self.__actionToIndex(action)
        col = self.__stateToIndex(state)
        self.__data[row, col] = value 
        return f"Updated at {self.__allStates[col]}, {self.__allActions[row]}.\nWrote value: {value}\n"   
    
    def getQValue(self, state, action):
        return self.__data[self.__actionToIndex(action),
                           self.__stateToIndex(state)]
    
    def getActionWithMaxQValue(self, state):
        col = self.__stateToIndex(state)
        index = self.__data.argmax(axis=0)[col]
        return self.__allActions[index]
    
    def getMaxQValueOfState(self, state):
        col = self.__stateToIndex(state)
        return np.amax(self.__data, axis=0)[col]
        
    def getRandomAction(self):
        return choice(self.__allActions)
        

    def writeQTableToFile(self):
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
       
    def randomize(self): # just for testing
        for row in range(len(self.__data)):
            for col in range(len(self.__data[row])):
                self.__data[row, col] = random()
        
    
        
    
    
    
    


if __name__ == '__main__':
                #  Lower Bounds     Upper Bounds     Increment for each
    stateShape = [[0, 0, 0],       [1, 99, 999],     [1, 30, 100]]     #    [[0, 40, 0],       [1, 99, 999],     [1, 30, 300]]
    actionShape = [30,               90,               5]
    
    qtable = QTable(stateShape, actionShape)
    qtable.randomize()
    
    # qtable.stateToIndex("169337")
    
    # for i in range(5):
    #     rs = "{:06d}".format(randint(int("040000"), int("199999")))
    #     print("random state: ", rs)
    #     print("action w max Q: ", qtable.getActionWithMaxQValue(rs))
    # qtable.updateAt("023423", "67", 69.69)
    print(qtable.getMaxQValueOfState("169337"))
    qtable.writeQTableToFile()
    
    # qtable.stateToIndex("166345")
    
    
    # Desision not to use mapping/ to use mapping
    # check shape is 0-00-000
    