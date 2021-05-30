import numpy as np
from random import randint


class QTable:
    def __init__(self, statesRange: list, actionRange: list, stateGroupsSize: int, actionGroupSize: int) -> None:
        # Validate all parameters
        self.__stateRange = self.__validateRange(statesRange)
        self.__actionRange = self.__validateRange(actionRange)
        self.__stateGroupSize = self.__validateGroupSize(stateGroupsSize)
        self.__actionGroupSize = self.__validateGroupSize(actionGroupSize)
        
        # provide feedback if any parameters are invalid
        if  self.__stateRange == [] or self.__actionRange == []:
            print("Table NOT created: range invalid")
            return None
        if self.__stateGroupSize == 0 or self.__actionGroupSize == 0:
            print("Table NOT created: group size invalid")
            return None
        
        # initialise the table
        self.__numRows, self.__numCols = self.__calcNumRowsAndCols()
        self.__data = np.zeros((self.__numRows, self.__numCols), dtype=float)
        
        np.set_printoptions(precision=3, suppress=True, linewidth=120) # just to make to output look decent
        
        print(f"{self.__numRows} x {self.__numCols} Table created")
        

    @staticmethod
    def __validateRange(theRange: list) -> list:
        if len(theRange) != 2:
            return []
        for i in range(len(theRange)):
            try:
                theRange[i] = int(theRange[i])
            except ValueError:
                print(f"range bound: {theRange[i]} is not an integer")
                return []
            
        if theRange[0] < theRange[1]:
            return theRange
        else:
            print("lower bound cannot be >= upper bound")
            return []
              
    
    @staticmethod
    def __validateGroupSize(size: int) -> int:
        try:
            size = int(size)
        except ValueError:
            print(f"{size} is not a valid size for a group")
            size = 0
        return size
        
    
    def __calcNumRowsAndCols(self) -> tuple:
        stateRangeWidth =  self.__stateRange[1] - self.__stateRange[0]
        actionRangeWidth = self.__actionRange[1] - self.__actionRange[0]
        
        numRows = actionRangeWidth // self.__actionGroupSize + 1
        numCols = stateRangeWidth // self.__stateGroupSize + 1
            
        return numRows, numCols
    
    def __actionToIndex(self, action: int) -> int:
        return action // self.__actionGroupSize
    
    def __stateToIndex(self, state: int) -> int:
        return state // self.__stateGroupSize
    
    def __indexToAction(self, index: int) -> int:
        return index * self.__actionGroupSize
    
    def __stateGivenIsValid(self, state: int) -> bool:
        if state in range(self.__stateRange[0], self.__stateRange[1]+1):
            return True
        else:
            print(f"state was outside the range specified: {state}")
            return False
        
    def __actionGivenIsValid(self, action: int) -> bool:
        if action in range(self.__actionRange[0], self.__actionRange[1]+1):
            return True
        else:
            print(f"action is outside the range specified {action}")
            return False
    
    def update(self, state: int, action: int, value: float) -> None:
        if self.__stateGivenIsValid(state) and self.__actionGivenIsValid(action):
            row = self.__actionToIndex(action)
            col = self.__stateToIndex(state)
            self.__data[row, col] = value
        else:
            print("table not updated")
        
    def getQValue(self, state: int, action: int) -> float:
        if self.__stateGivenIsValid(state) and self.__actionGivenIsValid(action):
            row = self.__actionToIndex(action)
            col = self.__stateToIndex(state)
            return self.__data[row,col]
        else:
            print("location not found on Q table")
            return 0.0
        
    def getActionWithMaxQValue(self, state: int) -> int:
        if self.__stateGivenIsValid(state):
            col = self.__stateToIndex(state)
            index = self.__data.argmax(axis=0)[col]
            return self.__indexToAction(index)
        else:
            print("couldn't find max Qvalue")
            return self.__actionRange[0] # lowest possible action (stop the car)
        
    def getRandomAction(self) -> int:
        row = randint(0, self.__numRows-1)
        return self.__indexToAction(row)      
        
    def printTable(self):
        print(self.__data) 
    
    
        
    
        
    
# table = QTable(["0","180"], [0,200], "10", 10)
# print(table.getActionWithMaxQValue(134587))

# table2 = QTable([0,0], [10,100], 1, 1)
# table3 = QTable(["1","5"], ["5","20"], 1, 1)

# table.update(37, 63, 3.415)
# print(table.getActionWithMaxQValue(67))
# print(table.getActionWithMaxQValue(119))
# print(table.getActionWithMaxQValue(30))

# Testing
if __name__ == '__main__':
    from random import random
    
    # fill the table with random values to test
    table = QTable([0,60], ["0","100"], 10, "20")
    for action in range(0,120, 20):
        for state in range(0,70, 10):
            table.update(state, action, random())
            
    # Test 1:
    print("\nTest 1")
    errorTable = QTable([0,0], [0,100], 1, 1)
    errorTable = QTable(["Four","ten"], ["5", 2], 1, 1)
    table.printTable()
    
    # Test 2:
    print("\nTest 2")
    print(table.getQValue(56, 12))
    print(table.getQValue(200, 4))
    print(table.getQValue(4,200))
    print(table.getQValue("four", "five"))
    
    # Test 3:
    print("\nTest 3")
    for state in range(0, 70, 10):
        print(table.getActionWithMaxQValue(state))
    
    # Test 4:
    print("\nTest 4")
    for i in range(3):
        print(table.getRandomAction())
    
    
    # print()
    # table.printTable()





    

        
        

# @staticmethod
#     def __validateDigits(sev: int, dist: int, speed: int) -> list:
#         valids = [sev, dist, speed]
#         for i in valids:
#             try:
#                 i = int(i)
#             except ValueError:
#                 print(f"{i} is not a valid number of digits")
#                 i = 0
#             finally:
#                 if i < 0:
#                     print(f"{i} is not a valid number of digits")
#                     i = 0
#         return valids
