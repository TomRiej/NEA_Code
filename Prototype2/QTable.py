from Constants import *

import numpy as np
from random import choice


class QTable:
    def __init__(self) -> None:
        """starts by validating the constants for state and action shapes. From this, 
        the number of rows and column can be calculated and an emtpy numpy array can be
        initialised for my QTable.
        """
        # validate the constants (raises ValueError if invalid)
        self.__validateStateAndActionShape()
        
        # state iterations per catagory is needed for O(1) mapping between states and indices.
        self.__stateIterationsPerCatagory = [len(range(STATE_SHAPE[0][x],
                                                       STATE_SHAPE[1][x] + 1,
                                                       STATE_SHAPE[2][x])) for x in range(3)]
        
        self.__allActions = [str(x) for x in range(ACTION_SHAPE[0],
                                                   ACTION_SHAPE[1] + 1,
                                                   ACTION_SHAPE[2])]
        
        numCols = np.product(self.__stateIterationsPerCatagory)
        numRows = len(self.__allActions)
        # dtype can be experimented with if i need more/less precision
        self.__data  = np.zeros((numRows, numCols), dtype="float32")

    # ==================== Private ========================================    
    @staticmethod              
    def __actionToIndex(action: str) -> int:
        """maps the action onto the correct index in my QTable in constant time complexity

        Args:
            action (str): the action that is guarenteed to be valid: (action passed into here
            was recently obtained via getRandomAction or getActionWithMaxQValue and not modified)

        Returns:
            int: the index of that action (row) in the __data numpy array
        """
        return (int(action) - ACTION_SHAPE[0]) // ACTION_SHAPE[2]        
          
    def __stateToIndex(self, state: str) -> int:
        """maps the state onto the correct index in my QTable in constant time complexity

        Args:
            state (str): the 6 digit state that is assumed to be valid (should be validated
            before being passed into here) The program won't crash if the state is invalid,
            but the returned index may not be accurate.

        Returns:
            int: the index of that state (column) in the __data numpy array
        """
        itersOfSeverity = (int(state[0]) - STATE_SHAPE[0][0]) // STATE_SHAPE[2][0]
        index = itersOfSeverity * np.product(self.__stateIterationsPerCatagory[1:])
        itersOfDistance = (int(state[1:3]) - STATE_SHAPE[0][1]) // STATE_SHAPE[2][1]
        index += itersOfDistance * self.__stateIterationsPerCatagory[2]
        index += (int(state[-3:]) - STATE_SHAPE[0][2]) // STATE_SHAPE[2][2]
        return index
    
    @staticmethod
    def __validateStateAndActionShape() -> None:
        """Validates the STATE_SHAPE and ACTION_SHAPE constants so they 
        allow the format decided in my design section.

        Raises:
            ValueError: shape doesn't have valid length 3
            ValueError: inner list doesn't have valid length 3
            ValueError: value in state shape isn't integer
            ValueError: value in action shape isn't integer
            ValueError: lower bound >= upper bound for states
            ValueError: incrementor for states is zero
            ValueError: lower bound >= upper bound for actions
            ValueError: incrementor for action is zero
        """
        validLength = 3
        # Validate shapes are len 3
        if not len(STATE_SHAPE) == len(ACTION_SHAPE) == validLength:
            raise ValueError("QTable", "state shape or action shape not a valid length of 3:\n"+
                             f"state shape: {STATE_SHAPE}\naction shape: {ACTION_SHAPE}")
        
        for i in range(validLength):
            # Validate inner list length to 3
            if len(STATE_SHAPE[i]) != validLength:
                raise ValueError("QTable", "inner list not a valid length of 3: "+
                                            f"{STATE_SHAPE[i]}")
                
            # Test for integers
            # first all the states (2D so requires nested loop)
            for j in range(validLength):
                if not isinstance(STATE_SHAPE[i][j], int):
                    raise ValueError("QTable", "Values in the state shape must be stored as "+
                                                f"integers, but '{STATE_SHAPE[i][j]}' is of "+
                                                f"type '{type(STATE_SHAPE[i][j])}'")
            # then the actions
            if not isinstance(ACTION_SHAPE[i], int):
                raise ValueError("QTable", "Values in the action shape must be stored as "+
                                            f"integers, but '{ACTION_SHAPE[i]}' is of type "+
                                            f"'{type(ACTION_SHAPE[i])}'")
        
        # Validating the bounds and incrementors
        # we needed to make sure all the values are integers so we can compare them using ><==
        # first the states (2D so requires nested loop)
        for i in range(validLength):
            # Validate lower bound < upper bound
            if not STATE_SHAPE[0][i] < STATE_SHAPE[1][i]:
                raise ValueError("QTable", f"Lower bound '{STATE_SHAPE[0][i]}' cannot be >= "+
                                            f"upper bound '{STATE_SHAPE[1][i]}' (state shape)")
            
            # Validate incrementor > 0
            if not STATE_SHAPE[2][i] > 0:
                raise ValueError("QTable", "incrementor in state shape must be > 0: "+
                                            f"'{STATE_SHAPE[2][i]}'")
        # then the actions
        if not ACTION_SHAPE[0] < ACTION_SHAPE[1]:
            raise ValueError("QTable", f"Lower bound '{ACTION_SHAPE[0]}' cannot be >= "+
                                        f"upper bound '{ACTION_SHAPE[1]}' (action shape)")
        if not ACTION_SHAPE[2] > 0:
            raise ValueError("QTable", "incrementor in action shape must be > 0: "+
                                        f"'{ACTION_SHAPE[2]}'")  
                   
    # ==================== Public ======================================== 
    def getActionWithMaxQValue(self, state: str) -> str:
        """returns the valid action string which has the highest QValue associated with it for
        the specified state.

        Args:
            state (str): the 6 digit state string (assumed to be valid)

        Returns:
            str: the action string with the highest Qvalue associated with it
        """
        # argmax() returns a list of indices with the maximum values associated with them along
        # a given axis: 0 for columns. Then we index into the action we're interested in
        return self.__allActions[self.__data.argmax(axis=0)[self.__stateToIndex(state)]]
    
    def getMaxQValue(self, state: str) -> float:
        """return the maximum Qvalue of the specified state (coloumn)

        Args:
            state (str): the 6 digit state string (assumed to be valid)

        Returns:
            float: the maximum QValue of the column
        """
        # np.amax() returns a list of the maximum values along a given axis: 0 is for columns
        # then we index this list to find the max value of the column we're interested in
        return np.amax(self.__data, axis=0)[self.__stateToIndex(state)]
    
    def getQValue(self, state: str, action: str) -> float:
        """returns the QValue at the specified state and action location on the Qtable

        Args:
            state (str): the 6 digit state string (assumed to be valid)
            action (str): the action (guaranteed to be valid)

        Returns:
            float: the QValue
        """
        return self.__data[self.__actionToIndex(action),
                           self.__stateToIndex(state)]
    
    def getRandomAction(self) -> str:
        """returns a random valid action from the QTable

        Returns:
            str: the random action
        """
        return choice(self.__allActions)
    
    def update(self, state: str, action: str, value: float) -> None:
        """updates the QTable at the specified action and state location with the specified
        value.

        Args:
            state (str): the 6 digit state string (assumed to be valid)
            action (str): the action string (guarenteed to be valid)
            value (float): the new QValue that needs to be written
        """
        self.__data[self.__actionToIndex(action), self.__stateToIndex(state)] = value
    
    @staticmethod
    def validateState(state: str) -> bool:
        """validates the state passed in agains the state shape constant to make sure it is
        within all the upper and lower bounds

        Args:
            state (str): the 6 digit state string

        Returns:
            bool: True if the state is valid, False otherwise
        """
        if not STATE_SHAPE[0][0] <= int(state[0]) <= STATE_SHAPE[1][0]:
            return False
        elif not STATE_SHAPE[0][1] <= int(state[1:3]) <= STATE_SHAPE[1][1]:
            return False
        elif not STATE_SHAPE[0][2] <= int(state[-3:]) <= STATE_SHAPE[1][2]:
            return False
        return True
    
    
    @staticmethod
    def __getallStatesFromShape(shape: list) -> list:
        states = []
        for s in range(shape[0][0], shape[1][0]+1, shape[2][0]):
            for d in range(shape[0][1], shape[1][1]+1, shape[2][1]):
                for v in range(shape[0][2], shape[1][2]+1, shape[2][2]):
                    states.append(f"{s}{d:02d}{v:03d}")
        return states
    
    def writeTableToFile(self):
        with open("QTable.txt", "w") as f:
            allStates = self.__getallStatesFromShape(STATE_SHAPE)
            f.write("   |  "+",   ".join(allStates))
            f.write("\n---"+"----------"*len(allStates))
            for i, action in enumerate(self.__allActions):
                formatted = []
                for col in self.__data[i]:
                    if col >= 0:
                        formatted.append(f"{col:.2E}")
                    else:
                        formatted.append(f"{col:.1E}")
                        
                f.write(f"\n{action} | "+"  ".join(formatted))
    
    
    
    # ==================== tests
    # @staticmethod
    # def __getallStatesFromShape(shape: list) -> list:
    #     states = []
    #     for s in range(shape[0][0], shape[1][0]+1, shape[2][0]):
    #         for d in range(shape[0][1], shape[1][1]+1, shape[2][1]):
    #             for v in range(shape[0][2], shape[1][2]+1, shape[2][2]):
    #                 states.append(f"{s}{d:02d}{v:03d}")
    #     return states
    
    # def test(self):
    #     allstates = self.__getallStatesFromShape(STATE_SHAPE)
    #     t = "034265"
    #     i = self.__stateToIndex(t)
    #     print(len(self.__data[0]))
    #     print(len(allstates))
    #     print(t, allstates[i])
    #     # print(self.__data[4, i])
        
        
    
    


if __name__ == '__main__':
    table = QTable()
    
    for i in range(199999 + 1):
        state = "{:06d}".format(i)
        print(f"State {state} validated returns {table.validateState(state)}")

    