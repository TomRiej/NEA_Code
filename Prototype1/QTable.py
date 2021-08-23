import numpy as np
from random import randint, random


class QTable:
    def __init__(self, stateShape, actionShape) -> None:
        self.__stateShape = self.__validateShape(stateShape)
        self.__actionShape = self.__validateShape(actionShape)
        
        # if invalid state: raise error, else contine
        
        self.__stateIterationsPerCatagory = [(self.__stateShape[1][0]+1 - self.__stateShape[0][0]) // self.__stateShape[2][0],
                                      (self.__stateShape[1][1]+1 - self.__stateShape[0][1]) // self.__stateShape[2][1],
                                      (self.__stateShape[1][2]+1 - self.__stateShape[0][2]) // self.__stateShape[2][2]]
        
        self.__allStates = self.__getallStatesFromShape(self.__stateShape)
        self.__allActions = [str(x) for x in range(self.__actionShape[0],
                                                   self.__actionShape[1]+1, 
                                                   self.__actionShape[2])]
        
        self.__numCols = len(self.__allStates)
        self.__numRows = len(self.__allActions)
        self.__data = np.zeros((self.__numRows, self.__numCols), dtype=np.float64)
        np.set_printoptions(precision=3, suppress=True, linewidth=120) # just to make to output look decent
        
    @staticmethod
    def __validateShape(shape):
        return shape
    
    @staticmethod
    def __getallStatesFromShape(shape):
        states = []
        for s in range(shape[0][0], shape[1][0]+1, shape[2][0]):
            for d in range(shape[0][1], shape[1][1]+1, shape[2][1]):
                for v in range(shape[0][2], shape[1][2]+1, shape[2][2]):
                    states.append(f"{s}{d:02d}{v:03d}")
        return states
    
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
        print(action, "->", self.__allActions[index])
        return action
    
        
    
    
    
    


if __name__ == '__main__':
                #  Lower Bounds     Upper Bounds     Increment for each
    stateShape = [[0, 40, 0],       [1, 99, 999],     [1, 20, 100]]
    actionShape = [30,           90,        5]
    
    qtable = QTable(stateShape, actionShape)